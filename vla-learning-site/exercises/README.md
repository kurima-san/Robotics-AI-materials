# 小さな実験で理解する

第27章と一緒に使う、実機・API・外部データ不要の教材です。Python 3.10以上を想定します。ロボットは動かしません。

## 1. 温度とsoftmax（追加ライブラリ不要）

サイトのルートで実行します。

```bash
python exercises/temperature_demo.py
python exercises/temperature_demo.py --logits 3 1 0 --temperatures 0.5 1 2 4
```

先に「温度を上げたら最大候補の順位と他の候補の確率はどうなるか」を予想してください。表示されるentropyの単位はnatsです。学習は行いません。

## 2. 蒸留（PyTorch / CPU）

既存のロボット開発環境を壊さないよう、別の仮想環境を推奨します。Windowsでは必要に応じて `python` を `py` に読み替えます。

```bash
python -m venv .venv
```

Windowsのコマンドプロンプトでは `.venv\Scripts\activate`、macOS/Linuxでは `source .venv/bin/activate` で有効化し、CPU用PyTorchを入れます。

```bash
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python exercises/toy_distillation.py
python exercises/toy_distillation.py --temperature 2 --output results/t2-seed7.json
python exercises/toy_distillation.py --temperature 4 --output results/t4-seed7.json
```

CPU向けwheelの対応はOSとPythonの版に依存します。インストールが合わないときは公式案内で選択してください。https://pytorch.org/get-started/locally/

教師は幅64・隠れ層2段、生徒は初期設定で幅12・隠れ層1段の小さなネットです。入力は2次元、出力は3クラスです。教師を学習した後で固定し、**同一の生徒の初期重み、学習データ、更新回数**を使ってCEのみとKD付きで比較します。教師分布を事前計算するため、生徒の学習時間には教師の事前計算時間は含まれません。蒸留の総工程コストを比較するベンチマークではありません。

損失は次の式です。

```text
(1 - alpha) * CE(student_logits, labels)
+ alpha * T^2 * KL(teacher_distribution || student_distribution)
```

学習・検証・テストを分け、チェックポイントの選択は検証精度で行います。テスト精度を見ながら設定を選び続けないでください。seedを変えた評価も重要です。**蒸留が必ず勝つとは限りません。** 推論時間はCPUのバッチ256入力の中央値であり、VLAやGPUの速度の予測には使えません。

主な引数：`--seed`、`--temperature`、`--alpha`、`--student-width`、`--train-size`、`--teacher-epochs`、`--student-epochs`。まず一つだけ変更して比較します。`--output` の既存ファイルは上書きしません。

一次資料：
- Hinton et al., Distilling the Knowledge in a Neural Network: https://arxiv.org/abs/1503.02531
- PyTorch Knowledge Distillation Tutorial: https://docs.pytorch.org/tutorials/beginner/knowledge_distillation_tutorial.html

## 3. データ契約を監査する（追加ライブラリ不要）

```bash
python exercises/dataset_audit.py
python exercises/dataset_audit.py exercises/sample_episodes.csv
```

合成CSVの20行を検査します。`camera_frame` は仮の画像識別子で、対応する画像ファイルはありません。`timestamp_s` はepisode内の開始からの秒数、`command_x/y` は教材上の正規化された指令値、`measured_x/y` は仮の観測値です。指令と観測は同一のものではありません。

検出対象は必須列・欠損・非有限数、episode内の時刻の非昇順、同一episodeや画像識別子のsplit混在、指令の範囲逸脱です。正常なら終了コード0、問題があれば1、実行引数や読み込みエラーなら2です。**LeRobot形式への変換器でも、実機の単位や安全性の検証器でもありません。**

CSVをコピーして、時刻の逆転、`NaN`、`command_x=2`、同一episodeのsplit変更などを一つずつ加え、検出できることを確認してください。実機の指令範囲は教材の `[-1, 1]` とは別に定めます。

## 実験メモの型

```text
仮説：
変更した一項目：
固定した条件（seed / split / 初期値 / 更新回数）：
評価指標：
結果：
解釈と次に確かめること：
```
