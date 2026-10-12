#!/usr/bin/env python3
"""Build static HTML and NotebookLM sources from JSON. Python 3.10+, stdlib only."""
from __future__ import annotations
import html, json, math, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'content/course.json').read_text(encoding='utf-8'))
REFS=json.loads((ROOT/'content/sources.json').read_text(encoding='utf-8'))
LESSONS=DATA['lessons']; MODULES=DATA['modules']; GLOSSARY=DATA['glossary']; DATE=DATA['edition']
# Correct the label: V and L are conditions, not mandatory serial conversion stages.
MODULES[4]['en']='VISION + LANGUAGE → ACTION'
E=lambda value:html.escape(str(value),quote=True)
def write(path:str,text:str):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def paras(text:str)->str:return ''.join(f'<p>{E(p)}</p>' for p in text.split('\n\n') if p.strip())
def keys(l):return list(dict.fromkeys(l['refs']+[r for s in l['sections'] for r in s['refs']]))
def cite(l,refs):return ''.join(f'<a class="citation" href="#l{l["id"]:02d}-ref-{E(k)}" aria-label="出典 {keys(l).index(k)+1}">[{keys(l).index(k)+1}]</a>' for k in refs)
def minutes(l):return max(4,math.ceil((len(l['lead'])+sum(len(s['body']) for s in l['sections'])+len(l['example'])+len(l['pitfall']))/400)+2)
def prompt(l):
 return f'''日本語で、通勤中に学ぶための解説動画を作成してください。\n対象はロボットの開発経験はあるが、深層学習を基礎から整理したい学習者です。\n今回の範囲は「第{l['id']:02d}章 {l['title']}」だけです。他章全体の概説へ広げないでください。\n最初に「{l['desc']}」という問いを提示してください。\n構成は、身近なたとえ → 正確な定義 → 仕組み → G1でノベルティを渡す例 → よくある誤解 → 復習の順にしてください。\n数式を長く読み上げず、記号の意味を日本語で説明してください。略語は初出で正式名称と読み方を添えてください。\n画面を見続けなくても分かるよう、図の関係をナレーションでも説明してください。「この図のとおり」だけで済ませないでください。\n資料中の実装上の提案や仮の数値例と、論文・公式実装の事実を区別してください。一般化や安全性を保証する表現は避けてください。\n最後に確認問題を2問出し、少し考える区切りのあとで答えと理由を説明してください。\n5〜8分程度に収まる密度を目安にし、短くなる場合も定義・具体例・誤解の訂正は省かないでください。正確な尺の指定ができない場合は、内容の一貫性を優先してください。\n出典にない数値、成功率、最新モデル名を追加しないでください。資料の確認日は{DATE}です。'''
PROMPTS=[dict(id=l['id'],text=prompt(l)) for l in LESSONS]
SEARCH=[dict(id=l['id'],title=l['title'],desc=l['desc'],text=' '.join([l['title'],l['desc'],l['lead'],*l['tags'],*[s['body'] for s in l['sections']]])) for l in LESSONS]
write('assets/search.js','window.COURSE_SEARCH='+json.dumps(SEARCH,ensure_ascii=False)+';\nwindow.COURSE_PROMPTS='+json.dumps(PROMPTS,ensure_ascii=False)+';\n')
CSS=(ROOT/'assets/style.css').read_text(encoding='utf-8')
JS=(ROOT/'assets/app.js').read_text(encoding='utf-8')

def head(title,description='',prefix='',inline=False):
 style=f'<style>{CSS}</style>' if inline else f'<link rel="stylesheet" href="{prefix}assets/style.css">'
 return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light dark"><meta name="theme-color" content="#143d32"><meta name="description" content="{E(description)}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(description)}"><title>{E(title)} | VLA Learning Path</title>{style}</head>'''
def scripts(prefix='',inline=False):
 if inline:
  srch='window.COURSE_SEARCH='+json.dumps(SEARCH,ensure_ascii=False).replace('</','<\\/')+';window.COURSE_PROMPTS='+json.dumps(PROMPTS,ensure_ascii=False).replace('</','<\\/')+';'
  return f'<script>{srch}</script><script>{JS}</script>'
 return f'<script src="{prefix}assets/search.js" defer></script><script src="{prefix}assets/app.js" defer></script>'
def sidebar(page,prefix='',current=None):
 nav=f'<a class="side-link {"active" if page=="home" else ""}" href="{prefix}index.html"><span class="nav-num">◫</span>学習ロードマップ</a>'
 nav+='<div class="side-label">LEARNING PATH</div>'
 for m in MODULES:
  active=current and current['module']==m['id']
  nav+=f'<a class="side-link {"active" if active else ""}" href="{prefix}index.html#module-{m["id"]}"><span class="nav-num mono">{m["id"]:02d}</span>{E(m["title"])}</a>'
  if active:
   nav+='<div class="nav-sub">'
   for l in LESSONS:
    if l['module']==m['id']:
     nav+=f'<a class="side-link {"active" if current["id"]==l["id"] else ""}" href="{prefix}lessons/{l["id"]:02d}.html"><span class="nav-dot" data-nav-dot="{l["id"]}"></span>{l["id"]:02d} {E(l["title"])}</a>'
   nav+='</div>'
 nav+='<div class="side-label">YOUR STUDY KIT</div>'
 for slug,label,icon in [('notebooklm','NotebookLMで動画化','↗'),('glossary','用語集','Aa'),('sources','論文・一次資料','↗'),('progress','学習履歴・復習','✓'),('setup','公開と編集の手順','⌘')]:
  nav+=f'<a class="side-link {"active" if page==slug else ""}" href="{prefix}{slug}.html"><span class="nav-num">{icon}</span>{label}</a>'
 return f'''<aside class="sidebar" id="sidebar" aria-label="学習メニュー"><a class="brand" href="{prefix}index.html"><span class="brand-mark">V</span><span><strong>VLA Learning Path</strong><small>FROM CONCEPT TO ACTION</small></span></a><nav class="side-scroll">{nav}</nav><div class="side-progress"><div class="progress-heading"><span>学習の進み具合</span><strong data-progress-count>0 / 28</strong></div><div class="progress-track"><div class="progress-fill" data-progress-fill></div></div><small>このブラウザに保存 · 外部送信なし</small></div></aside><div class="mobile-backdrop" id="mobile-backdrop"></div>'''
def shell(title,content,page='home',prefix='',current=None,description='VLAをゴールに、深層学習・LLM・蒸留を基礎から学ぶ日本語教材。'):
 titlecrumb='学習ロードマップ' if page=='home' else (f'LESSON {current["id"]:02d}' if current else title)
 return head(title,description,prefix)+f'''<body data-prefix="{prefix}" {f'data-lesson="{current["id"]}"' if current else ''}><a class="skip" href="#main">本文へ移動</a>{sidebar(page,prefix,current)}<div class="workspace"><header class="topbar"><button class="icon-button mobile-toggle" id="menu-toggle" aria-label="学習メニューを開閉" aria-expanded="false" aria-controls="sidebar">☰</button><span class="breadcrumb">LEARNING HUB <span aria-hidden="true"> / </span> {E(titlecrumb)}</span><div class="top-search"><span class="search-symbol" aria-hidden="true">⌕</span><input type="search" id="site-search" placeholder="章・キーワードを検索" aria-label="全章を検索" autocomplete="off"></div><a class="text-link" href="{prefix}notebooklm.html">NotebookLMへ ↗</a><button class="icon-button" data-theme-toggle>ダーク</button></header><div class="search-results" id="search-results" hidden aria-label="検索結果"></div><div class="reading-progress"></div><noscript><div class="nojs">本文・用語集・出典はそのまま読めます。検索・学習履歴・操作デモにはJavaScriptが必要です。確認問題は各問の「答え」を開いてください。</div></noscript><main class="main" id="main">{content}</main><footer class="site-footer"><span>VLA Learning Path · 学ぶ、確かめる、実装へつなぐ。</span><span>一次資料確認 {DATE} · <a href="{prefix}sources.html">出典と更新方針</a></span></footer></div><div class="toast" id="toast" role="status" aria-live="polite" hidden></div>{scripts(prefix)}</body></html>'''

def card(l,standalone=False):
 href=f'#lesson-{l["id"]:02d}' if standalone else f'lessons/{l["id"]:02d}.html'
 return f'''<a class="lesson-card" href="{href}"><div class="card-meta"><span class="mono">LESSON {l['id']:02d} <span aria-hidden="true">/</span> 約{minutes(l)}分</span><span class="done-label" data-done-badge="{l['id']}"></span></div><div class="card-title">{E(l['title'])}</div><p class="card-description">{E(l['desc'])}</p><div class="card-bottom">{''.join(f'<span class="tag">{E(t)}</span>' for t in l['tags'][:3])}<span class="card-arrow" aria-hidden="true">↗</span></div></a>'''
def hero():
 return '''<section class="hero"><div><div class="eyebrow"><span class="status-dot"></span> ROBOT LEARNING, ONE STEP AT A TIME</div><h1>見る、理解する、<br><span>そして、動かす。</span></h1><p class="hero-description">深層学習の基礎からLLM、蒸留、VLAへ。<br>「G1がノベルティを人に渡す」を題材に、<br>モデルの仕組みと実機へのつながりを学ぶ。</p><div class="actions"><a class="btn btn-primary" data-resume href="lessons/01.html">第01章から始める →</a><a class="btn btn-quiet" href="notebooklm.html">通勤を、学習時間に ↗</a></div></div><div class="hero-visual" aria-label="画像と言語を条件に行動候補を生成するVLAの模式的な整理"><div class="visual-kicker">VISION + LANGUAGE → ACTION</div><div class="flow-nodes"><div class="flow-node"><span class="flow-letter">V</span><div><strong>Vision</strong><small>画像から、状況を捉える</small></div></div><div class="flow-node"><span class="flow-letter">L</span><div><strong>Language</strong><small>指示から、目的を捉える</small></div></div><div class="flow-node"><span class="flow-letter">A</span><div><strong>Action</strong><small>条件を合わせ、行動を生成</small></div></div></div><p class="flow-note">身体状態や履歴も入力に。制御・安全層は別途設計。</p></div></section>'''
def home():
 text=hero()+'''<div class="stat-row"><div class="stat"><strong>28<em>章</em></strong><span>基礎から実機設計まで</span></div><div class="stat"><strong>84<em>問</em></strong><span>理解を確かめる</span></div><div class="stat"><strong>72<em>語</em></strong><span>日本語・英語の用語集</span></div><div class="stat"><strong>7<em>部</em></strong><span>迷わない学習順序</span></div></div><section class="feature-band"><div><h2>読むだけで終わらせない。通勤で、もう一度。</h2><p>各章の教材と動画化プロンプトを同梱。NotebookLMには「取り込み専用ページ」またはMarkdownを渡します。</p></div><a class="btn btn-small" href="notebooklm.html">動画化の手順を見る ↗</a></section><div class="section-top"><h2>あなたの学習ロードマップ</h2><p>初回は01から順番に。知っている章は飛ばしても構いません。</p></div>'''
 for m in MODULES:
  text+=f'<section class="module-section" id="module-{m["id"]}"><div class="module-heading"><span class="module-number mono">{m["id"]:02d}</span><div><h3>{E(m["title"])}</h3><p>{E(m["desc"])}</p></div></div><div class="lesson-grid">'+''.join(card(l) for l in LESSONS if l['module']==m['id'])+'</div></section>'
 text+='''<div class="course-note"><strong>この教材の位置づけ</strong><br>ロボット開発の経験を生かして、深層学習の前提から理解するための教材です。原理・一次資料の事実と、G1に向けた設計例を区別しています。掲載モデルは学ぶための代表例であり、最新版の網羅的ランキングではありません。実機を動かすコードや、安全性を保証する手順は含みません。読む時間は本文量からの概算です。</div>'''
 return shell('見る、理解する、そして動かす。',text)

def references(l):
 out='<ol class="source-list">'
 for k in keys(l):
  r=REFS[k]
  out+=f'<li id="l{l["id"]:02d}-ref-{E(k)}"><a href="{E(r["url"])}" target="_blank" rel="noopener noreferrer">{E(r["title"])}</a> <span>（{E(r["year"])}）</span><span class="source-desc">{E(r["note"])} 確認日：{DATE}</span></li>'
 return out+'</ol>'
def demo_markup(kind,uid):
 base=f'<section class="demo" data-demo="{kind}" id="demo-{uid}"><div class="box-label">TRY IT · 数値を動かして理解する</div>'
 if kind=='temperature':
  base+=f'''<h2>温度を上げると、分布はどう変わる？</h2><p>固定したlogit [3, 1, 0]にsoftmax(z/T)を適用します。これは学習ではなく分布の計算です。</p><label for="temperature-{uid}">温度 T <output>1.0</output></label><input id="temperature-{uid}" type="range" min="0.3" max="5" step="0.1" value="1">'''
  for label in ['候補 A','候補 B','候補 C']:
   base+=f'<div class="probability-row"><span>{label}</span><div class="probability-track"><div class="probability-bar"></div></div><span class="probability-value">—</span></div>'
  base+='<p class="note">Tが高いほど分布は平らになりますが、同じlogitなら候補の順位は変わりません。</p>'
 elif kind=='lora':
  base+=f'''<h2>rankと追加パラメータ数</h2><p>4096×4096の一つの行列へのLoRAの概算。基盤重み・活性・optimizerの総メモリ計算ではありません。</p><label for="rank-{uid}">rank r <output>8</output></label><input id="rank-{uid}" type="range" min="1" max="64" step="1" value="8"><div class="demo-metrics"><div class="demo-metric">元の行列<strong data-base>16,777,216</strong></div><div class="demo-metric">追加パラメータ<strong data-extra>65,536</strong></div></div><p>元の行列に対する追加分：<strong data-ratio>0.39%</strong></p>'''
 elif kind=='chunk':
  base+=f'''<h2>予測は32時刻。何時刻を実行する？</h2><p>H=32、サンプル周波数50Hz、推論100msを仮定した教材例です。色の付いた先頭部分を実行します。</p><label for="chunk-{uid}">実行長 K <output>8</output></label><input id="chunk-{uid}" type="range" min="1" max="32" step="1" value="8"><div class="chunk-strip" aria-label="32時刻の予測と実行部分"></div><div class="demo-metrics"><div class="demo-metric">K時刻分の実行時間<strong data-exec-time>0.16秒</strong></div><div class="demo-metric">実行時間 − 仮定の推論時間<strong data-budget>60 ms</strong></div></div><p class="demo-warning" data-chunk-status>JavaScriptで時間関係を計算します。</p><p class="note">非同期に計算を重ねる単純な時間予算の例です。同期的に順番に処理する場合や、観測の古さ・安全性はこの差だけでは判断できません。</p>'''
 elif kind=='gradient':
  base+=f'''<h2>重みを1ステップずつ更新する</h2><p>損失 L=(w−2)²、初期値w=−2。目標はw=2です。学習率を大きくすると何が起きるでしょうか。</p><label for="rate-{uid}">学習率 η <output>0.10</output></label><input id="rate-{uid}" type="range" min="0.01" max="1.20" step="0.01" value="0.10"><div class="demo-metrics"><div class="demo-metric">重み w<strong data-weight>−2.0000</strong></div><div class="demo-metric">損失 L<strong data-loss>16.0000</strong></div></div><div class="actions"><button class="btn btn-primary btn-small" data-step>1ステップ学習する</button><button class="btn btn-small" data-gradient-reset>リセット</button></div><div class="gradient-history" aria-live="polite"></div>'''
 return base+'</section>'

def quizzes(l,standalone=False,source=False):
 n=l['id']; anchor=f'quiz-{n:02d}' if standalone else 'quiz'
 out=f'<section class="quiz-section" id="{anchor}"><div class="box-label">CHECK YOUR UNDERSTANDING</div><h2>理解を確かめる、3つの問い</h2>'
 if not source:out+='<p class="note">答えを選ぶと理由を表示します。間違えたときは本文へ戻り、自分の言葉で説明してみましょう。</p>'
 for i,q in enumerate(l['quiz']):
  if source:
   out+=f'<p><strong>問{i+1}：{E(q["question"])}</strong><br>答え：{E(q["options"][q["answer"]])}<br>理由：{E(q["why"])}</p>'
  else:
   out+=f'<fieldset class="quiz" data-key="{n}-{i}" data-answer="{q["answer"]}"><legend>{i+1}. {E(q["question"])}</legend><div class="quiz-options">'
   for j,option in enumerate(q['options']):out+=f'<button type="button" class="quiz-option" data-choice="{j}" aria-pressed="false"><span class="option-letter">{chr(65+j)}</span><span>{E(option)}</span></button>'
   out+=f'</div><p class="quiz-feedback" data-explanation="{E(q["why"])}" aria-live="polite" hidden></p><noscript><details><summary>答えと解説</summary><p>{E(q["options"][q["answer"]])}。{E(q["why"])}</p></details></noscript></fieldset>'
 return out+'</section>'

def lesson_body(l,interactive=True,standalone=False):
 n=l['id'];out=f'<p class="chapter-lead">{E(l["lead"])}</p><div class="prose">'
 for i,sec in enumerate(l['sections']):
  out+=f'<section id="l{n:02d}-s{i+1}"><h3>{E(sec["title"])}</h3>{paras(sec["body"])}'
  if sec['refs']:out+=f'<p class="inline-source">この節の参考：{cite(l,sec["refs"])}</p>'
  else:out+='<p class="inline-source">教材上の整理・設計例。</p>'
  out+='</section>'
 out+='</div>'
 out+=f'<div class="formula-box"><div class="box-label">ONE FORMULA · 数式の読み方</div><div class="formula-expression">{E(l["formula"]["expression"])}</div><p>{E(l["formula"]["explanation"])}</p></div>'
 if l['demo'] and interactive:out+=demo_markup(l['demo'],f'l{n:02d}')
 out+=f'<div class="example-box"><div class="box-label">IN PRACTICE · G1で考える設計例</div><p>{E(l["example"])}</p></div><div class="pitfall-box"><div class="box-label">COMMON MISCONCEPTION · よくある誤解</div><p>{E(l["pitfall"])}</p></div><div class="takeaways-box"><h2>この章で持ち帰ること</h2><ul>'+''.join(f'<li>{E(t)}</li>' for t in l['takeaways'])+'</ul></div>'
 out+=quizzes(l,standalone=standalone,source=not interactive)
 out+=f'<section id="sources-{n:02d}"><div class="box-label">PRIMARY SOURCES</div><h2 style="font-size:21px">出典と、次に読む資料</h2>{references(l)}</section>'
 if interactive:
  out+=f'<section class="notes-box"><h2>自分の言葉で、30秒の説明を。</h2><p>「つまり何か」「G1にどう関係するか」を書いてみましょう。メモはこのブラウザだけに保存されます。</p><label class="note" for="note-{n:02d}">第{n:02d}章の学習メモ</label><textarea class="lesson-note" data-note-id="{n}" id="note-{n:02d}" maxlength="20000" placeholder="例：蒸留と量子化の違いは…"></textarea></section>'
  out+=f'<div class="lesson-bottom"><button class="btn btn-primary" data-complete="{n}" aria-pressed="false">この章を学習済みにする</button><button class="btn" data-copy-target="prompt-{n:02d}">動画化の指示をコピー ↗</button></div><textarea id="prompt-{n:02d}" hidden>{E(prompt(l))}</textarea>'
 return out

def chapter(l):
 n=l['id'];m=MODULES[l['module']-1]
 out=f'<div class="lesson-layout"><article><header class="lesson-header"><div class="eyebrow">LESSON {n:02d} / {E(m["en"])}</div><h1>{E(l["title"])}</h1><p class="lesson-deck">{E(l["desc"])}</p><div class="lesson-meta"><span>読む目安 約{minutes(l)}分</span><span>確認問題 3問</span><span>確認日 {DATE}</span></div><div class="actions no-print"><a class="btn btn-small" href="../notebooklm/chapters/{n:02d}.md" download>教材を保存 .md ↓</a><button class="btn btn-small" data-copy-url>章のURLをコピー</button><button class="btn btn-small" data-print>印刷</button></div></header>'
 out+=lesson_body(l)
 out+='<nav class="lesson-nav" aria-label="前後の章">'
 out+=(f'<a href="{n-1:02d}.html"><small>← PREVIOUS</small>{E(LESSONS[n-2]["title"])}</a>' if n>1 else '<a href="../index.html"><small>← ROADMAP</small>学習ロードマップへ</a>')
 out+=(f'<a href="{n+1:02d}.html"><small>NEXT →</small>{E(LESSONS[n]["title"])}</a>' if n<28 else '<a href="../progress.html"><small>REVIEW →</small>学習の振り返りへ</a>')
 out+='</nav></article><aside class="lesson-toc"><strong>ON THIS PAGE</strong>'
 for i,sec in enumerate(l['sections']):out+=f'<a href="#l{n:02d}-s{i+1}">{E(sec["title"])}</a>'
 out+=f'<a href="#quiz">確認問題</a><a href="#sources-{n:02d}">出典と次の資料</a><div class="reader-tools"><span>文字サイズ</span><button data-font="-1" aria-label="本文を小さく">A−</button><button data-font="1" aria-label="本文を大きく">A+</button></div></aside></div>'
 return shell(l['title'],out,'lesson','../',l,l['desc'])

def md_lesson(l):
 n=l['id'];lines=[f'# 第{n:02d}章 {l["title"]}',f'\n{l["desc"]}',f'\n教材の確認日：{DATE}\n',
 '対象：ロボット開発に関心があり、深層学習を基礎から理解したい学習者。\n位置づけ：基礎概念と代表研究を学ぶ教材。実機向けの設計例は動作や安全性の保証ではない。\n',l['lead']]
 for sec in l['sections']:
  lines.extend([f'\n## {sec["title"]}',sec['body']])
  if sec['refs']:lines.append('参考：'+', '.join(f'[{k}]' for k in sec['refs']))
  else:lines.append('（教材上の整理・設計例）')
 lines.extend(['\n## 数式の読み方',l['formula']['expression'],l['formula']['explanation'],'\n## G1で考える設計例',l['example'],'\n## よくある誤解',l['pitfall'],'\n## この章で持ち帰ること'])
 lines.extend('- '+t for t in l['takeaways'])
 lines.append('\n## 確認問題と答え')
 for i,q in enumerate(l['quiz']):lines.append(f'\n問{i+1}：{q["question"]}\n答え：{q["options"][q["answer"]]}\n理由：{q["why"]}')
 associated=[g for g in GLOSSARY if g['lesson']==n]
 if associated:
  lines.append('\n## 用語と読み方')
  lines.extend(f'- {g["term"]}（{g["reading"]}）：{g["definition"]}' for g in associated)
 lines.append('\n## 出典・追加で読む一次資料')
 for k in keys(l):
  r=REFS[k];lines.append(f'- [{k}] {r["title"]}（{r["year"]}）\n  {r["url"]}\n  読むポイント：{r["note"]}\n  確認日：{DATE}')
 return '\n\n'.join(lines)+'\n'

def page_header(kicker,title,desc):return f'<header class="page-header"><div class="eyebrow">{E(kicker)}</div><h1>{E(title)}</h1><p>{E(desc)}</p></header>'

def notebook_page():
 out=page_header('LEARN ON YOUR COMMUTE','通勤を、復習の時間に。','NotebookLMで章ごとの日本語解説動画を作るための教材と指示を用意しました。このサイト自体は動画生成や外部サービスへのアップロードを行いません。')
 out+='''<section class="content-panel"><h2>まずは、1章を1本に。</h2><ol class="steps"><li><strong>学びたい章のMarkdownを保存する</strong>下の一覧から <code>01.md</code> などを保存します。GitHubへ公開する前でも利用できます。全章をまとめた資料もありますが、最初の生成は一章に絞ると範囲を保ちやすくなります。</li><li><strong>NotebookLMのソースへ追加する</strong>Web版でノートブックを作り、Markdownをアップロードします。URLで渡す場合は、GitHub Pagesで公開した章のページ、または <code>all.html</code> を追加します。</li><li><strong>下の章別プロンプトをコピーする</strong>生成対象以外の章まで広げないよう、章の番号と学びたい問いを指定しています。複数のソースを入れた場合は、今回必要なソースを選んでください。</li><li><strong>Studio → 動画解説 → 日本語の「解説」を選ぶ</strong>利用できる形式、言語、カスタム指示欄を確認し、下の指示を設定して生成します。表示や利用条件はアカウント・版により異なる場合があります。</li><li><strong>内容を確認してから通勤で復習する</strong>数式の読み方、用語、事実と設計例の区別を確認します。視聴後にサイトの確認問題へ戻り、学習済みとメモを残しましょう。</li></ol><p class="note">Google公式ヘルプではサービス名が「Gemini Notebook」と表記される場合があります。この教材ではユーザーの呼称に合わせNotebookLMと表記しています。日本語で学ぶ場合は、利用可能な日本語対応の解説形式を選んでください。確認時点のヘルプではシネマティック形式は英語のみです。<a href="https://support.google.com/notebooklm/answer/16454555?hl=ja" target="_blank" rel="noopener noreferrer">動画解説の公式ヘルプ ↗</a></p></section>'''
 out+='''<section class="content-panel"><h2>URLを一つ渡すときの注意</h2><p><strong>トップページのURLだけでは、リンク先の全章は取り込まれません。</strong>Googleの説明では、URL取り込みの対象はそのHTMLページの本文で、画像・埋め込み動画・入れ子のウェブページは含まれません。このサイトはJavaScriptなしでも本文が存在する静的HTMLです。</p><div class="actions"><a class="btn btn-primary" href="all.html">全章の取り込み専用ページ ↗</a><a class="btn" href="notebooklm/ALL_CHAPTERS.md" download>全章Markdown ↓</a><a class="btn" href="notebooklm/ALL_CHAPTERS.txt" download>全章テキスト ↓</a></div><p class="note" style="margin-top:15px">公開後のURLの形：<code>https://YOURNAME.github.io/vla-learning-site/all.html</code><br>これは例です。実際にはGitHub Pagesに表示されたURLを使ってください。取り込んだあと、第01章と第28章の見出しがソースに含まれるか確認します。公開サイトを更新した際は、取り込まれた内容も再確認し、必要に応じて再取り込みしてください。<a href="https://support.google.com/notebooklm/answer/16215270?hl=ja" target="_blank" rel="noopener noreferrer">ソース取り込みの公式ヘルプ ↗</a></p></section>'''
 out+='<section class="content-panel prompt-box"><h2>動画化の指示をコピー</h2><label for="prompt-lesson">今回学ぶ章</label><select class="prompt-select" id="prompt-lesson">'
 for l in LESSONS:out+=f'<option value="{l["id"]}">{l["id"]:02d} · {E(l["title"])}</option>'
 out+=f'</select><label class="note" for="video-prompt">カスタム指示（必要に応じて編集できます）</label><textarea id="video-prompt">{E(prompt(LESSONS[0]))}</textarea><div class="actions"><button class="btn btn-primary" data-copy-target="video-prompt">指示をコピー</button><a class="btn" id="selected-source" href="notebooklm/chapters/01.md" download>この章の教材 .md ↓</a></div><p class="note" style="margin-top:14px">5〜8分は指示上の目安で、正確な生成尺は保証できません。動画はサイトを録画したものではなく、取り込んだ資料からAIが再構成する解説です。画面を見ない復習用には音声解説の利用も考えられます。</p></section>'
 out+='<section class="content-panel"><h2>章別の教材</h2><p>教材本文・確認問題の答え・用語の読み・出典を一つにまとめています。動画化の指示は別ファイルです。</p><div class="chapter-downloads">'
 for l in LESSONS:out+=f'<a class="chapter-download" href="notebooklm/chapters/{l["id"]:02d}.md" download><span class="mono">{l["id"]:02d}</span><span>{E(l["title"])}</span><span>MD ↓</span></a>'
 out+='</div></section><section class="content-panel"><h2>4章ずつ、まとまりで復習する</h2><p>各部は4章です。まとめ動画を作る際は、定義をすべて詰め込むより章同士の関係を比較する指示に変えてください。</p><div class="chapter-downloads">'
 for m in MODULES:out+=f'<a class="chapter-download" href="notebooklm/modules/{m["id"]:02d}.md" download><span class="mono">PART {m["id"]:02d}</span><span>{E(m["title"])}</span><span>MD ↓</span></a>'
 out+='</div></section><p class="course-note">AI生成の解説には誤りが含まれる場合があります。特に「必ず安全」「追加学習不要」「すべての機体で動く」といった強い表現は元の教材と一次資料で確認してください。NotebookLM内での取り込み・動画生成は、このサイトの動作テストには含まれていません。</p>'
 return shell('NotebookLMで動画化',out,'notebooklm')

def glossary_page():
 out=page_header('THE LANGUAGE OF ROBOT LEARNING','用語で、つまずかない。','日本語・英語・読み方から引ける72語。短い定義を確認し、詳しい章へ戻れます。')
 out+='<label class="note" for="glossary-search">用語・読み方・説明を検索</label><input class="wide-input" type="search" id="glossary-search" placeholder="例：蒸留、distillation、ディスティレーション"><p class="note" id="glossary-count">72語を表示</p><div class="glossary-grid">'
 for i,g in enumerate(GLOSSARY):out+=f'<article class="glossary-item" id="term-{i+1}"><h2>{E(g["term"])}</h2><p class="reading">{E(g["reading"])}</p><p>{E(g["definition"])}</p><a href="lessons/{g["lesson"]:02d}.html">第{g["lesson"]:02d}章で詳しく読む →</a></article>'
 return shell('用語集',out+'</div>','glossary')

def sources_page():
 out=page_header('READ THE ORIGINAL','学びの根拠へ、戻れる。','40件の論文・研究プロジェクト・公式ドキュメント。説明は本教材向けに書き下ろし、外部資料や図版の全文は転載していません。')
 out+='<section class="content-panel"><h2>「事実」と「設計例」を区別する</h2><p>論文の主張や実装の対応範囲は、その出典とモデル世代の範囲で記述しています。G1の状態機械、試験手順、数値例は教材上の提案です。成功率・性能順位・安全性を外挿しません。</p><p>確認日は <strong>'+DATE+'</strong> です。最新版の網羅ではありません。特にGitHubのmainブランチ、必要メモリ、モデルへのアクセス条件、Googleの画面は変わる可能性があります。実装時には公式の版と条件を再確認してください。</p></section><section class="content-panel">'
 for i,(k,r) in enumerate(REFS.items()):
  out+=f'<article class="reference-card" id="ref-{E(k)}"><div class="reference-meta">SOURCE {i+1:02d} / {E(r["year"])} / 確認 {DATE}</div><h2><a href="{E(r["url"])}" target="_blank" rel="noopener noreferrer">{E(r["title"])} ↗</a></h2><p>{E(r["note"])}</p>'
  related=[l for l in LESSONS if k in keys(l)]
  if related:out+='<div class="reference-meta">関連する章：'+', '.join(f'<a href="lessons/{l["id"]:02d}.html">{l["id"]:02d}</a>' for l in related)+'</div>'
  out+='</article>'
 return shell('出典・一次資料',out+'</section>','sources')

def progress_page():
 out=page_header('PAUSE. RECALL. CONTINUE.','学んだことを、自分の言葉に。','学習済み・確認問題・メモは、このブラウザ内に保存します。アカウント連携や端末間の自動同期はありません。')
 out+='<div class="stat-row"><div class="stat"><strong style="font-size:23px" data-progress-count>0 / 28</strong><span>学習済みの章</span></div><div class="stat"><strong style="font-size:23px" data-quiz-count>0 / 84</strong><span>直近の回答が正解の問題</span></div></div><div class="actions"><a class="btn btn-primary" data-resume href="lessons/01.html">第01章から始める →</a></div><section class="content-panel"><h2>もう一度、確認したい章</h2><div class="review-list" id="review-list"><p class="note">JavaScriptを有効にすると、このブラウザで記録した不正解の章を表示します。</p></div></section>'
 out+='''<section class="content-panel"><h2>学習データを持ち運ぶ</h2><p>会社のPCからスマートフォンへ移るときや、ブラウザの保存領域を消す前に書き出してください。JSONには学習メモが含まれるので、公開リポジトリには入れないでください。</p><div class="backup-panel"><button class="btn btn-primary" data-export-progress>学習データを書き出す ↓</button><label class="btn" for="import-progress">学習データを読み込む ↑</label><input type="file" id="import-progress" accept=".json,application/json" hidden><button class="btn" data-reset-progress>すべてリセット</button></div><p class="note">読込時には現在のデータを置き換える確認を表示します。ローカルで開いたHTMLと公開URL、公開サイトと単体版は、保存領域を共有しない場合があります。プライベートブラウズや保存領域の制限時は、履歴が残らない場合があります。</p><p class="demo-warning" id="storage-warning" hidden>この環境では保存領域を利用できません。画面を閉じる前に学習データを書き出してください。</p></section><section class="content-panel"><h2>通勤での一巡</h2><ol class="steps"><li><strong>一章を読む</strong>最後の三つの要点だけを見て、説明できるか確認します。</li><li><strong>動画で関係をつかみ直す</strong>聞き慣れない略語や、分からなかったところを短いメモに残します。</li><li><strong>確認問題へ戻る</strong>答えだけでなく、なぜ他の選択肢が違うかも説明します。</li><li><strong>一つだけ実装に結びつける</strong>「これはG1のどの部分か」を一文で書きます。</li></ol></section>'''
 return shell('学習履歴・復習',out,'progress')

def setup_page():
 out=page_header('PUBLISH YOUR LEARNING HUB','GitHubへ置いて、そのまま使う。','ビルド済みのHTML・CSS・JavaScriptを同梱しています。公開するだけならNode.js、npm、サーバ、APIキーは不要です。')
 out+='''<section class="content-panel"><h2>まずローカルで開く</h2><p>ZIPを展開し、<code>index.html</code> をChromeやEdgeなどのブラウザで開きます。すべての本文は静的HTMLです。外部フォントやCDNは使っていません。ローカルの保存制約を避ける場合は、Pythonの簡易サーバを使用できます。</p><pre>cd vla-learning-site\npython -m http.server 8000</pre><p>ブラウザで <code>http://localhost:8000/</code> を開きます。外部への通信は、出典リンクなどを自分で開く場合を除き不要です。</p></section>'''
 out+='''<section class="content-panel"><h2>GitHub Pagesで公開する</h2><ol class="steps"><li><strong>空のリポジトリを作る</strong>名前の例は <code>vla-learning-site</code>。個人情報を含まない教材なので、公開する構成としてPublicを想定しています。Pagesの利用可否はアカウント条件も確認してください。</li><li><strong>展開したフォルダの「中身」をpushする</strong><code>index.html</code> がリポジトリ直下に来るようにします。ZIPファイル自体を置くだけではサイトとして公開されません。ファイル数が多いため、下のGit手順が確実です。</li><li><strong>Settings → Pagesを開く</strong>Build and deploymentのSourceを <code>Deploy from a branch</code> にし、Branchを <code>main</code>、Folderを <code>/ (root)</code> にして保存します。</li><li><strong>表示された公開URLを開く</strong>Pagesの公開完了を確認し、トップ・章・NotebookLM取り込み専用ページを開きます。URLは <code>https://YOURNAME.github.io/vla-learning-site/</code> のような形です。</li></ol><p class="note"><a href="https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site" target="_blank" rel="noopener noreferrer">GitHub公式の公開設定 ↗</a></p><pre>git init\ngit add .\ngit commit -m "Add Japanese VLA learning site"\ngit branch -M main\ngit remote add origin https://github.com/YOURNAME/vla-learning-site.git\ngit push -u origin main</pre><p class="note">新規の空リポジトリを想定した例です。YOURNAMEは自分のユーザー名へ変更します。GitHub認証は自分の環境で行ってください。トークンやパスワードを教材ファイルへ書かないでください。</p></section>'''
 out+='''<section class="content-panel"><h2>1ファイルだけで公開する方法</h2><p><code>standalone.html</code> は全28章・確認問題・操作デモ・用語集を含む単体版です。別の空リポジトリへ <code>index.html</code> に名前を変えて置き、同じPages設定で公開できます。この単体版は章別ファイルやMarkdownのダウンロード機能を持たないため、NotebookLMにはその公開URLか、ZIP内の教材Markdownを渡してください。</p></section>'''
 out+='''<section class="content-panel"><h2>教材を追加・修正する</h2><p>教材の元データは <code>content/course.json</code>、出典は <code>content/sources.json</code> です。本文・問題・答え・用語を編集し、以下を実行します。Python 3.10以上の標準ライブラリだけで生成できます。</p><pre>python tools/build.py</pre><p>生成されたHTMLとNotebookLM用Markdownを一緒にcommitしてください。公開時のビルドは不要です。見た目は <code>assets/style.css</code>、操作は <code>assets/app.js</code> で編集できます。</p><p class="note">本文のsource of truthはJSONです。生成済みHTMLだけを直接編集すると、再生成でその変更が消えます。章数を増減する場合は、学習履歴の章数・クイズ数なども合わせて変更してください。</p></section>'''
 out+='''<section class="content-panel"><h2>公開前の確認</h2><p>教材以外の社内データ、人物が写る記録、認証情報、学習メモを含めないでください。本教材にはAPIキー、外部サービスの認証、トラッキング、ロボットを駆動する処理はありません。GitHubへのアップロードやNotebookLMでの生成は利用者が行う手順です。</p></section>'''
 return shell('公開と編集の手順',out,'setup')

def collection(standalone=False):
 if standalone:
  out=head('全28章を一つのファイルで', '深層学習からLLM・蒸留・VLAまで学ぶ日本語教材の単体版。',inline=True)
  out+='''<body data-standalone="true"><a class="skip" href="#main">本文へ移動</a><header class="collection-topbar"><a href="#main">VLA Learning Path</a><nav style="display:flex;gap:12px;align-items:center"><a href="#contents">目次</a><a href="#glossary">用語集</a><button class="icon-button" data-theme-toggle>ダーク</button><button class="icon-button" data-export-progress>履歴を書出</button></nav></header><main class="collection-main" id="main"><div class="eyebrow">STANDALONE EDITION · NO INSTALL REQUIRED</div><h1 class="collection-title">見る、理解する、<br>そして、動かす。</h1><p class="chapter-lead">深層学習からLLM、蒸留、VLAへ。G1がノベルティを渡す例で学ぶ、全28章の日本語教材です。</p><section class="feature-band"><div><h2>単体HTML版</h2><p>ネット接続なしで本文・問題・操作デモを利用できます。学習履歴はこのブラウザに保存されます。NotebookLMへ渡す場合は、このHTMLを公開したURL、または配布ZIP内のMarkdownを利用します。HTMLファイルの直接アップロードは前提にしていません。</p></div></section><p class="note">確認日：'''+DATE+'''。教材上の設計例は、実機での動作や安全性を保証しません。GitHubやNotebookLMへの自動アップロードは行いません。</p><h2 id="contents">学習の目次</h2>'''
 else:
  out=head('NotebookLM取り込み用・全28章','全28章の教材本文・問題と答え・用語・一次資料。リンク先の自動巡回は不要。',inline=True)
  out+='<body><main class="source-only" id="main"><h1>VLA Learning Path — 全28章の教材本文</h1><p>このページ内に全章の本文があります。リンク先を巡回しなくても教材を読み取れます。動画化の指示や学習履歴は含みません。</p><p>確認日：'+DATE+'。対象：ロボット開発を背景に深層学習を基礎から理解したい学習者。代表研究を選んだ教材であり、最新版の網羅・実機安全性の保証ではありません。</p><h2>目次</h2>'
 out+='<ol class="collection-toc">'+''.join(f'<li><a href="#lesson-{l["id"]:02d}">{l["id"]:02d} {E(l["title"])}</a></li>' for l in LESSONS)+'</ol>'
 for l in LESSONS:
  out+=f'<article class="collection-lesson" id="lesson-{l["id"]:02d}"><div class="eyebrow">PART {l["module"]:02d} / LESSON {l["id"]:02d}</div><h2>第{l["id"]:02d}章 {E(l["title"])}</h2><p class="lesson-deck">{E(l["desc"])}</p>'+lesson_body(l,interactive=standalone,standalone=True)+'</article>'
 out+='<section id="glossary" style="padding-top:35px"><h2>用語集と読み方</h2>'
 if standalone:out+='<label class="note" for="glossary-search">用語・読み方を検索</label><input class="wide-input" type="search" id="glossary-search" placeholder="例：蒸留、LoRA"><p class="note" id="glossary-count">72語を表示</p>'
 out+='<div class="glossary-grid">'
 for g in GLOSSARY:out+=f'<article class="glossary-item"><h3>{E(g["term"])}</h3><p class="reading">{E(g["reading"])}</p><p>{E(g["definition"])}</p><a href="#lesson-{g["lesson"]:02d}">第{g["lesson"]:02d}章へ →</a></article>'
 out+='</div></section>'
 if standalone:out+='<section class="content-panel"><h2>学習履歴とメモの管理</h2><p>このファイルで保存した履歴はブラウザ内にあります。端末を変える際は書き出し、別の端末で読み込んでください。メモには社内情報を書き込まないよう注意してください。</p><div class="backup-panel"><button class="btn" data-export-progress>学習履歴を保存 ↓</button><label class="btn" for="import-progress">履歴を読み込む ↑</label><input id="import-progress" type="file" accept=".json,application/json" hidden><button class="btn" data-reset-progress>履歴をリセット</button></div><p><span data-progress-count>0 / 28</span> 章を学習済み</p></section>'
 out+='</main>'
 if standalone:out+='<div class="toast" id="toast" role="status" aria-live="polite" hidden></div>'+scripts(inline=True)
 return out+'</body></html>'

def main():
 assert len(LESSONS)==28 and len(GLOSSARY)==72
 assert len({l['id'] for l in LESSONS})==28
 for l in LESSONS:
  assert len(l['quiz'])==3
  for q in l['quiz']:assert len(q['options'])==3 and q['answer'] in range(3)
  for k in keys(l):assert k in REFS
 write('index.html',home())
 for l in LESSONS:
  write(f'lessons/{l["id"]:02d}.html',chapter(l))
  write(f'notebooklm/chapters/{l["id"]:02d}.md',md_lesson(l))
  write(f'notebooklm/prompts/{l["id"]:02d}.txt',prompt(l)+'\n')
 allmd='# VLA Learning Path — 全28章\n\n確認日：'+DATE+'\n\nこのファイルは教材ソースです。章ごとの生成指示はnotebooklm/promptsに分離しています。\n\n'+'\n\n---\n\n'.join(md_lesson(l) for l in LESSONS)
 write('notebooklm/ALL_CHAPTERS.md',allmd)
 write('notebooklm/ALL_CHAPTERS.txt',allmd)
 for m in MODULES:write(f'notebooklm/modules/{m["id"]:02d}.md',f'# 第{m["id"]}部 {m["title"]}\n\n'+'\n\n---\n\n'.join(md_lesson(l) for l in LESSONS if l['module']==m['id']))
 for slug,func in [('notebooklm',notebook_page),('glossary',glossary_page),('sources',sources_page),('progress',progress_page),('setup',setup_page)]:write(slug+'.html',func())
 write('all.html',collection())
 write('standalone.html',collection(True))
 write('.nojekyll','')
 print(f'Built {len(LESSONS)} lessons, {sum(len(l["quiz"]) for l in LESSONS)} questions, {len(GLOSSARY)} terms, {len(REFS)} sources.')
 print(f'NotebookLM source: {len(allmd):,} characters.')
if __name__=='__main__':main()
