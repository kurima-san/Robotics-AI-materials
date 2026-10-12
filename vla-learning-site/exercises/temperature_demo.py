#!/usr/bin/env python3
"""温度付きsoftmaxを計算する。Python 3.10+ / 標準ライブラリのみ。"""
from __future__ import annotations
import argparse
import math


def softmax(logits: list[float], temperature: float) -> list[float]:
    if not logits or not all(math.isfinite(x) for x in logits):
        raise ValueError('logitsは空でない有限数のリストにしてください。')
    if not math.isfinite(temperature) or temperature <= 0:
        raise ValueError('temperatureは有限の正の数にしてください。')
    # 最大値を引き、expのオーバーフローを避ける。
    maximum = max(logits)
    weights = [math.exp((x - maximum) / temperature) for x in logits]
    total = sum(weights)
    return [x / total for x in weights]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--logits', type=float, nargs='+', default=[3.0, 1.0, 0.0])
    parser.add_argument('--temperatures', type=float, nargs='+', default=[0.5, 1.0, 2.0, 4.0])
    args = parser.parse_args()
    print(f'logits = {args.logits}\n温度を上げても、最大候補の順位は変わるでしょうか？\n')
    for temperature in args.temperatures:
        try:
            probs = softmax(args.logits, temperature)
        except ValueError as exc:
            parser.error(str(exc))
        entropy = -sum(p * math.log(p) for p in probs if p > 0)
        print(f'T={temperature:4.1f}  p=[{", ".join(f"{p:.4f}" for p in probs)}]'
              f'  sum={sum(probs):.6f}  entropy={entropy:.4f} nats')
    print('\nこれは分布の計算であり、教師・生徒の学習やLLM生成実験ではありません。')


if __name__ == '__main__':
    main()
