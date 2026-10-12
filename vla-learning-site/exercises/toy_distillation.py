#!/usr/bin/env python3
"""合成2次元分類で、同じ初期値の生徒をCEのみ/KD付きで比較するCPU教材。"""
from __future__ import annotations
import argparse
import copy
import json
import math
import platform
import statistics
import time
from pathlib import Path
try:
    import torch
    from torch import nn
    from torch.nn import functional as F
except ImportError as exc:
    raise SystemExit('PyTorchが必要です。exercises/README.mdを参照してください。') from exc


def make_data(count: int, seed: int) -> tuple[torch.Tensor, torch.Tensor]:
    generator = torch.Generator().manual_seed(seed)
    x = torch.rand(count, 2, generator=generator) * 4 - 2
    a, b = x[:, 0], x[:, 1]
    # 線形だけでは解けない境界を作る。全モデルで同じデータを共有する。
    scores = torch.stack((torch.sin(2 * a) + 0.6 * b,
                          torch.cos(2 * b) - 0.6 * a,
                          0.4 * (a.square() + b.square()) - 0.5), dim=1)
    y = scores.argmax(dim=1)
    # 少量のラベルノイズ。蒸留が必ず改善するように結果を選別しない。
    noisy = torch.rand(count, generator=generator) < 0.04
    noise_labels = torch.randint(0, 3, (count,), generator=generator)
    return x, torch.where(noisy, noise_labels, y)


def network(width: int, depth: int) -> nn.Sequential:
    layers: list[nn.Module] = [nn.Linear(2, width), nn.Tanh()]
    for _ in range(depth - 1):
        layers.extend([nn.Linear(width, width), nn.Tanh()])
    layers.append(nn.Linear(width, 3))
    return nn.Sequential(*layers)


@torch.inference_mode()
def accuracy(model: nn.Module, x: torch.Tensor, y: torch.Tensor) -> float:
    model.eval()
    return float((model(x).argmax(dim=1) == y).float().mean())


def train(model: nn.Module, train_x: torch.Tensor, train_y: torch.Tensor,
          val_x: torch.Tensor, val_y: torch.Tensor, epochs: int,
          teacher: nn.Module | None = None, temperature: float = 3.0,
          alpha: float = 0.5) -> tuple[nn.Module, float, float]:
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    best_score = -1.0
    best_weights = copy.deepcopy(model.state_dict())
    soft_targets = None
    if teacher is not None:
        teacher.eval()
        # 教師に勾配を流さず、同一入力での教師分布を固定する。
        with torch.no_grad():
            soft_targets = F.softmax(teacher(train_x) / temperature, dim=1).detach()
    started = time.perf_counter()
    for _ in range(epochs):
        model.train()
        optimizer.zero_grad(set_to_none=True)
        logits = model(train_x)
        hard_loss = F.cross_entropy(logits, train_y)
        if soft_targets is None:
            loss = hard_loss
        else:
            # KL(P_teacher || P_student)。入力はlog確率、targetは通常の確率。
            soft_loss = F.kl_div(F.log_softmax(logits / temperature, dim=1),
                                 soft_targets, reduction='batchmean') * temperature**2
            loss = (1 - alpha) * hard_loss + alpha * soft_loss
        if not torch.isfinite(loss):
            raise RuntimeError('損失が有限ではありません。設定とデータを確認してください。')
        loss.backward()
        optimizer.step()
        score = accuracy(model, val_x, val_y)
        # チェックポイントの選択には検証データだけを使う。
        if score > best_score:
            best_score, best_weights = score, copy.deepcopy(model.state_dict())
    model.load_state_dict(best_weights)
    model.eval()
    return model, best_score, time.perf_counter() - started


@torch.inference_mode()
def inference_ms(model: nn.Module, batch: torch.Tensor) -> float:
    model.eval()
    for _ in range(10):
        model(batch)
    durations = []
    for _ in range(50):
        start = time.perf_counter_ns()
        model(batch)
        durations.append((time.perf_counter_ns() - start) / 1e6)
    return statistics.median(durations)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=7)
    parser.add_argument('--teacher-epochs', type=int, default=180)
    parser.add_argument('--student-epochs', type=int, default=120)
    parser.add_argument('--student-width', type=int, default=12)
    parser.add_argument('--train-size', type=int, default=4096)
    parser.add_argument('--temperature', type=float, default=3.0)
    parser.add_argument('--alpha', type=float, default=0.5, help='KD損失の混合率。0ならCEだけ。')
    parser.add_argument('--output', type=Path, help='任意の結果JSON。既存ファイルは上書きせず停止する。')
    args = parser.parse_args()
    if min(args.teacher_epochs, args.student_epochs, args.student_width, args.train_size) < 1:
        parser.error('epoch、width、train-sizeは正の整数にしてください。')
    if not math.isfinite(args.temperature) or args.temperature <= 0:
        parser.error('temperatureは有限の正の数にしてください。')
    if not math.isfinite(args.alpha) or not 0 <= args.alpha <= 1:
        parser.error('alphaは0以上1以下にしてください。')
    if args.output and args.output.exists():
        parser.error('出力先が既に存在します。別のファイル名を指定してください。')
    torch.manual_seed(args.seed)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    # 同じ生成分布から独立した乱数でtrain / validation / testを作る。
    train_x, train_y = make_data(args.train_size, args.seed + 100)
    val_x, val_y = make_data(1024, args.seed + 200)
    test_x, test_y = make_data(2048, args.seed + 300)
    teacher = network(64, 2)
    teacher, teacher_val, teacher_time = train(teacher, train_x, train_y, val_x, val_y,
                                              args.teacher_epochs)
    for parameter in teacher.parameters():
        parameter.requires_grad_(False)
    initial_student = network(args.student_width, 1)
    baseline = copy.deepcopy(initial_student)
    distilled = copy.deepcopy(initial_student)
    assert all(torch.equal(a, b) for a, b in zip(baseline.parameters(), distilled.parameters()))
    baseline, baseline_val, baseline_time = train(baseline, train_x, train_y, val_x, val_y,
                                                 args.student_epochs)
    distilled, distilled_val, distilled_time = train(distilled, train_x, train_y, val_x, val_y,
                                                      args.student_epochs, teacher,
                                                      args.temperature, args.alpha)
    models = [('teacher', teacher, teacher_val, teacher_time),
              ('student_ce', baseline, baseline_val, baseline_time),
              ('student_kd', distilled, distilled_val, distilled_time)]
    rows = []
    print('\nCPU / batch=256 / 同じ生徒の初期重み / 検証精度で重み選択\n')
    print(f'{"model":<13} {"params":>8} {"val acc":>9} {"test acc":>9} {"infer ms":>10} {"train s":>9}')
    # テストは選択済みモデルの報告時だけ参照する。
    for name, model, val_acc, train_time in models:
        row = dict(model=name, parameters=sum(p.numel() for p in model.parameters()),
                   validation_accuracy=val_acc, test_accuracy=accuracy(model, test_x, test_y),
                   median_inference_ms_batch256=inference_ms(model, test_x[:256]),
                   training_seconds=train_time)
        rows.append(row)
        print(f'{name:<13} {row["parameters"]:>8,} {val_acc:>9.3%} '
              f'{row["test_accuracy"]:>9.3%} {row["median_inference_ms_batch256"]:>10.4f} '
              f'{train_time:>9.3f}')
    result = dict(settings={k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
                  environment=dict(python=platform.python_version(), torch=torch.__version__,
                                   platform=platform.platform(), threads=1, device='cpu'),
                  results=rows)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
        print(f'\n保存: {args.output}')
    print('\n蒸留が勝つとは限りません。まず温度だけを変え、次にseedを変えて比較してください。')
    print('推論時間はこのCPU・小型モデル・バッチの参考値で、VLAやGPUのベンチマークではありません。')
    print('テスト結果を見ながら設定を選び続けるとテストへの過適合になります。設定選択は検証データで行います。')


if __name__ == '__main__':
    main()
