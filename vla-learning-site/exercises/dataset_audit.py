#!/usr/bin/env python3
"""教材CSVの時刻・split・指令値を点検する。実機の仕様検証器ではない。"""
from __future__ import annotations
import argparse
import csv
import math
from pathlib import Path

REQUIRED = ('episode_id', 'split', 'timestamp_s', 'camera_frame',
            'command_x', 'command_y', 'measured_x', 'measured_y')
NUMERIC = ('timestamp_s', 'command_x', 'command_y', 'measured_x', 'measured_y')
SPLITS = {'train', 'validation', 'test'}


def audit(path: Path, command_limit: float = 1.0) -> tuple[list[str], dict[str, int]]:
    problems: list[str] = []
    episodes: dict[str, str] = {}
    timestamps: dict[str, float] = {}
    frames: dict[str, str] = {}
    split_counts: dict[str, int] = {}
    rows = 0
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        headers = reader.fieldnames or []
        missing = set(REQUIRED) - set(headers)
        if missing:
            return ['必須列がありません: ' + ', '.join(sorted(missing))], {'rows': 0, 'episodes': 0}
        if len(headers) != len(set(headers)):
            return ['列名が重複しています。'], {'rows': 0, 'episodes': 0}
        for row in reader:
            rows += 1
            label = f'行{reader.line_num}'
            if None in row:
                problems.append(f'{label}: ヘッダーより列が多く、CSVの構造が不正です。')
            values = {key: (row.get(key) or '').strip() for key in REQUIRED}
            for key, value in values.items():
                if not value:
                    problems.append(f'{label}: {key} が欠損しています。')
            episode, split, frame = values['episode_id'], values['split'], values['camera_frame']
            if split not in SPLITS:
                problems.append(f'{label}: split={split!r} はtrain/validation/testのいずれかにしてください。')
            split_counts[split] = split_counts.get(split, 0) + 1
            if episode:
                if episode in episodes and episodes[episode] != split:
                    problems.append(f'{label}: 同じepisode {episode!r} に複数のsplitがあります。')
                episodes.setdefault(episode, split)
            # 同じ画像識別子が別splitに出現するケースも検出する。
            if frame:
                if frame in frames and frames[frame] != split:
                    problems.append(f'{label}: camera_frame={frame!r} が複数splitに出現しています。')
                frames.setdefault(frame, split)
            numbers: dict[str, float] = {}
            for key in NUMERIC:
                if not values[key]:
                    continue
                try:
                    value = float(values[key])
                    if not math.isfinite(value):
                        raise ValueError('非有限値')
                    numbers[key] = value
                except ValueError:
                    problems.append(f'{label}: {key} は有限の数値ではありません。')
            stamp = numbers.get('timestamp_s')
            if stamp is not None and episode:
                if stamp < 0:
                    problems.append(f'{label}: timestamp_s が負です。教材では開始からの秒を使います。')
                if episode in timestamps and stamp <= timestamps[episode]:
                    problems.append(f'{label}: episode={episode!r} の時刻が厳密な昇順ではありません。')
                timestamps[episode] = stamp
            for key in ('command_x', 'command_y'):
                if key in numbers and abs(numbers[key]) > command_limit:
                    problems.append(f'{label}: {key}={numbers[key]} が教材の指令範囲±{command_limit}を超えます。')
    if not rows:
        problems.append('データ行がありません。')
    stats = {'rows': rows, 'episodes': len(episodes),
             **{f'{key}_rows': split_counts.get(key, 0) for key in sorted(SPLITS)}}
    return problems, stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_path', nargs='?', type=Path,
                        default=Path(__file__).with_name('sample_episodes.csv'))
    parser.add_argument('--command-limit', type=float, default=1.0,
                        help='この教材の正規化指令値の絶対値上限。実機の物理単位ではない。')
    args = parser.parse_args()
    if not math.isfinite(args.command_limit) or args.command_limit <= 0:
        parser.error('command-limitは有限の正の値にしてください。')
    try:
        problems, stats = audit(args.csv_path, args.command_limit)
    except (OSError, UnicodeError, csv.Error) as exc:
        parser.error(f'CSVを読み込めません: {exc}')
    print(' / '.join(f'{key}={value}' for key, value in stats.items()))
    if problems:
        for problem in problems:
            print('[ERROR] ' + problem)
        print(f'\n{len(problems)}件の問題を検出しました。終了コード1。')
        return 1
    print('この教材の検査項目では問題を検出しませんでした。終了コード0。')
    print('画像ファイルの実在・単位の正しさ・実機の安全性・LeRobot仕様全体を保証する検査ではありません。')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
