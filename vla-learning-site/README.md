# VLA Learning Path

**見る、理解する、そして、動かす。**

深層学習の基礎からLLM、知識蒸留、VLA、ヒューマノイドへの接続までを学ぶ、日本語の静的HTML教材です。「G1がノベルティを人に渡す」を共通の設計例にしています。全28章、84問、用語集72語、一次資料40件。一次資料の確認日：2026-10-11。

## まず読む

ファイル一つで使う場合は **`standalone.html` をブラウザで開く**と、全28章・クイズ・デモ・メモを利用できます。公開用の通常サイトの入口は **`index.html`** です。本文はHTMLに直接入っており、JavaScriptを無効にしても読めます。

PCとスマートフォン向けレイアウト、全文キーワード検索、ダークモード、文字サイズ変更、学習済みの記録、クイズ、間違えた章の復習、章別メモ、学習データのJSON書き出し・読み込みを備えています。ブラウザの保存領域を消すと履歴も消えます。端末間の自動同期はありません。重要なメモは書き出して保管してください。ローカルファイルの保存動作はブラウザに依存するため、普段の利用にはGitHub Pagesを推奨します。

## GitHub Pagesに公開する

### 方法A：全機能版をGitで公開する

1. GitHubで空の公開リポジトリを作成します。名前の例は `vla-learning` です。この方法ではREADMEなどをGitHub側で自動作成せず、空にしてください。
2. **このREADMEと `index.html` があるフォルダ**で以下を実行します。`YOURNAME` とリポジトリ名を置き換えます。すでに別リポジトリを管理しているフォルダでは実行しないでください。

```bash
git init
git add .
git commit -m "Add VLA learning site"
git branch -M main
git remote add origin https://github.com/YOURNAME/vla-learning.git
git push -u origin main
```

3. GitHubの **Settings → Pages → Build and deployment** で、Sourceを **Deploy from a branch**、Branchを **main**、フォルダを **/(root)** にしてSaveします。
4. 公開処理の結果と、Pages画面に表示されたURLを確認します。`index.html` をさらに一段下のフォルダに入れないでください。リポジトリ直下に配置します。

公開URLの例は `https://YOURNAME.github.io/vla-learning/`、NotebookLM用はその末尾に `all.html` を付けたものです。これは説明用URLであり、実際の公開先ではありません。

公式手順： https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

### 方法B：ブラウザだけで最小公開する

`standalone.html` を **`index.html` に名前を変更**し、その1ファイルを空の公開リポジトリ直下にアップロードします。Pages設定は方法Aと同じです。HTML内にCSSとJavaScriptが入っているため、この1ファイルで全章を読めます。ただし章別Markdown、Python実験、通常版の管理ページは含まれません。NotebookLMへの取り込みには、配布物の `ALL_CHAPTERS.md` を別途使用してください。

通常版をまとめてアップロードする場合はファイル数が多いため、方法AのGitの利用が確実です。GitHubの画面表示や上限は変更されることがあります。

## NotebookLMで通勤用の動画にする

現在の公式ヘルプではGemini Notebookという表記も見られます。この教材ではユーザーになじみのあるNotebookLMという名称を使います。機能名や利用可否はアカウントと提供状況によって確認してください。

**トップページのURLだけでは全章を取り込めません。** 公式ヘルプではURL取り込みの対象は指定ページのHTML本文だけで、リンク先のページ・画像・埋め込み動画は対象外です。そのため専用の静的ページとテキスト教材を同梱しています。

| 目的 | 渡すもの |
| --- | --- |
| まず第01章の動画を作る | `notebooklm/chapters/01.md` |
| 4章ずつ一つの部を学ぶ | `notebooklm/modules/01.md` など |
| 全教材に質問する | `notebooklm/ALL_CHAPTERS.md` または `.txt` |
| 公開サイトのURLから取り込む | 公開先の `all.html` |
| 動画のカスタム指示 | `notebooklm/prompts/01.txt` など。教材ソースではなく指示欄に使う |

学習動画は、**一章ずつ**作るところから始めます。ソースを追加後、Studio → 動画解説 → カスタマイズで、日本語の「解説」を選び、該当章のプロンプトを貼り付けます。プロンプトはサイトの「NotebookLMで動画化」ページからもコピーできます。全章を一つの短い動画にすると概要だけになりやすいため、学習範囲を指定します。

プロンプトは5〜8分程度の密度を目安にしていますが、尺を保証しません。数式の意味を言葉で説明し、図を見ていなくても理解できるナレーション、G1の例、誤解の訂正、最後の復習を求めています。AI生成の動画は必ず教材と照合してください。シネマティックは確認日時点で英語のみと案内されているため、日本語の勉強には通常の「解説」を使います。

サイト更新後は、NotebookLM側のソースにも変更が反映されたか確認し、必要に応じて再取り込みしてください。このサイトはNotebookLM APIを呼び出さず、ファイルを自動送信せず、動画を自動生成しません。

公式資料：
- ソース取り込み： https://support.google.com/notebooklm/answer/16215270?hl=ja
- 動画解説： https://support.google.com/notebooklm/answer/16454555?hl=ja

## 学習の順番

| 部 | 章 | テーマ |
| --- | --- | --- |
| 1 | 01–04 | VLAまでの地図、テンソル、学習、汎化 |
| 2 | 05–08 | トークン、Attention、LLM、VLM |
| 3 | 09–12 | RAG、LoRA/QLoRA、蒸留、量子化/KV cache/MoE |
| 4 | 13–16 | 方策、行動表現、ACT、Diffusion Policy |
| 5 | 17–20 | Flow Matching、RT-2/OpenVLA、π系、GR00T |
| 6 | 21–24 | データ、閉ループ評価、遅延と安全、World Model |
| 7 | 25–28 | 推論モデル、G1のタスク設計、小型実験、論文の読み方 |

## ファイル構成と編集

```text
index.html                 通常版のトップ
lessons/01.html … 28.html   各章
all.html                   全章の取り込み専用ページ（JavaScript不要）
standalone.html            CSS/JS込みの一枚完結版
notebooklm.html             動画化手順とプロンプト選択
notebooklm/                 全章・部別・章別ソースと28個のプロンプト
glossary.html               用語集
sources.html                一次資料と確認日
progress.html               学習履歴・復習・バックアップ
setup.html                  公開・編集の説明
assets/                     ローカルCSS/JS
content/course.json         教材・クイズ・用語集の編集元
content/sources.json        一次資料の編集元
tools/build.py              静的ページ生成（Python標準ライブラリ）
exercises/                  ロボットを動かさないPython実験
.nojekyll                   GitHub Pagesで静的ファイルをそのまま配信
```

通常の閲覧や公開にPython、Node.js、ビルド処理は不要です。編集時は `content/course.json` と `content/sources.json` を変更し、次を実行します。

```bash
python tools/build.py
python -m http.server 8000 --bind 127.0.0.1
```

ブラウザで `http://127.0.0.1:8000/` を開きます。サーバを終了するには実行したターミナルでCtrl+Cを押します。CSSは `assets/style.css`、動作は `assets/app.js` を編集します。再生成するとHTMLとNotebookLM教材が更新されます。**生成後のHTMLだけを直接編集すると、次の生成で変更が失われます。**

教材の章数・問題数を変えるときは、JavaScript内の学習データ処理と固定の表示数も変更する必要があります。現版は28章・各3問の教材として設計されています。

## プライバシーと注意

外部のJavaScript、フォント、解析サービス、APIキーは不要です。学習履歴とメモはブラウザ内にだけ保存します。本文を公開リポジトリに置くと第三者にも読まれるため、社内情報・ログ・個人情報・認証情報を追加しないでください。外部の出典リンクを開く操作は、その外部サイトへのアクセスになります。

モデルの仕様、ライセンス、推奨GPU、NotebookLM/GitHubのUIは変わります。参考モデルは学習のための代表例であり、最新版のランキングやG1での動作保証ではありません。各章は一次資料の事実と本教材の設計例を分けています。実機への適用には別途リスク評価と管理された試験が必要です。
