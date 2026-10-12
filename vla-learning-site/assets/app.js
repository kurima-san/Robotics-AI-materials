/* Progressive enhancement: all lesson text is present without JavaScript. */
'use strict';
(() => {
  const $=(s,root=document)=>root.querySelector(s), $$=(s,root=document)=>Array.from(root.querySelectorAll(s));
  const KEY='vla-learning-path.v1';
  const defaults=()=>({version:1,done:{},notes:{},quiz:{},theme:'light',font:17,last:null});
  let state=defaults(), storageAvailable=true;
  function cleanState(raw){
    if(!raw||typeof raw!=='object'||Array.isArray(raw)||raw.version!==1) throw new Error('この教材の学習データではありません。');
    const out=defaults();
    for(let i=1;i<=28;i++){
      if(raw.done?.[i]===true)out.done[i]=true;
      if(typeof raw.notes?.[i]==='string')out.notes[i]=raw.notes[i].slice(0,20000);
      for(let j=0;j<3;j++){
        const key=`${i}-${j}`, v=raw.quiz?.[key];
        if(v&&Number.isInteger(v.choice)&&v.choice>=0&&v.choice<=2&&typeof v.correct==='boolean')out.quiz[key]={choice:v.choice,correct:v.correct};
      }
    }
    out.theme=raw.theme==='dark'?'dark':'light';
    out.font=[15,16,17,18,19,20,21].includes(raw.font)?raw.font:17;
    out.last=Number.isInteger(raw.last)&&raw.last>=1&&raw.last<=28?raw.last:null;
    return out;
  }
  try{const raw=localStorage.getItem(KEY);if(raw)state=cleanState(JSON.parse(raw));}catch(e){storageAvailable=false;}
  let toastTimer;
  function toast(message){const node=$('#toast');if(!node)return;node.textContent=message;node.hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>node.hidden=true,3500);}
  function save(){try{localStorage.setItem(KEY,JSON.stringify(state));storageAvailable=true;}catch(e){if(storageAvailable)toast('保存領域を利用できません。学習データを書き出して保管してください。');storageAvailable=false;}}
  function applySettings(){document.documentElement.dataset.theme=state.theme;document.documentElement.style.setProperty('--read-size',state.font+'px');$$('[data-theme-toggle]').forEach(b=>{b.textContent=state.theme==='dark'?'ライト':'ダーク';b.setAttribute('aria-label',state.theme==='dark'?'ライトモードに変更':'ダークモードに変更');});}
  applySettings();
  const lessonId=Number(document.body.dataset.lesson);
  if(lessonId){state.last=lessonId;save();}
  function lessonLink(id){return document.body.dataset.standalone==='true'?`#lesson-${String(id).padStart(2,'0')}`:(document.body.dataset.prefix||'')+`lessons/${String(id).padStart(2,'0')}.html`;}
  function renderProgress(){
    const count=Object.values(state.done).filter(Boolean).length;
    $$('[data-progress-count]').forEach(el=>el.textContent=`${count} / 28`);
    $$('[data-progress-fill]').forEach(el=>el.style.width=(count/28*100)+'%');
    $$('[data-complete]').forEach(btn=>{const id=btn.dataset.complete;btn.setAttribute('aria-pressed',String(!!state.done[id]));btn.textContent=state.done[id]?'✓ 学習済み（取り消す）':'この章を学習済みにする';});
    $$('[data-done-badge]').forEach(el=>{el.textContent=state.done[el.dataset.doneBadge]?'✓ 学習済み':'';});
    $$('[data-nav-dot]').forEach(el=>el.classList.toggle('done',!!state.done[el.dataset.navDot]));
    const resume=$('[data-resume]');if(resume){const id=state.last||1;resume.href=lessonLink(id);resume.textContent=state.last?`第${String(id).padStart(2,'0')}章の続きを読む →`:'第01章から始める →';}
    const quizCount=$('[data-quiz-count]');if(quizCount)quizCount.textContent=`${Object.values(state.quiz).filter(x=>x.correct).length} / 84`;
    renderReview();
  }
  renderProgress();
  $$('[data-theme-toggle]').forEach(b=>b.addEventListener('click',()=>{state.theme=state.theme==='dark'?'light':'dark';save();applySettings();}));
  $$('[data-font]').forEach(b=>b.addEventListener('click',()=>{state.font=Math.max(15,Math.min(21,state.font+Number(b.dataset.font)));save();applySettings();toast(`本文サイズ：${state.font}px`);}));
  $$('[data-complete]').forEach(b=>b.addEventListener('click',()=>{const id=b.dataset.complete;state.done[id]=!state.done[id];save();renderProgress();toast(state.done[id]?'学習済みにしました。':'学習済みを取り消しました。');}));
  $$('[data-note-id]').forEach(el=>{el.value=state.notes[el.dataset.noteId]||'';el.addEventListener('input',()=>{state.notes[el.dataset.noteId]=el.value.slice(0,20000);save();});});
  const menu=$('#menu-toggle'), sidebar=$('#sidebar'), backdrop=$('#mobile-backdrop');
  function closeMenu(){sidebar?.classList.remove('open');backdrop?.classList.remove('open');menu?.setAttribute('aria-expanded','false');}
  menu?.addEventListener('click',()=>{const open=sidebar.classList.toggle('open');backdrop.classList.toggle('open',open);menu.setAttribute('aria-expanded',String(open));});
  backdrop?.addEventListener('click',closeMenu);$$('a',sidebar||document.createElement('div')).forEach(a=>a.addEventListener('click',closeMenu));
  async function copyText(text){
    try{if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(text);}else{throw new Error('fallback');}toast('コピーしました。');}
    catch(e){const t=document.createElement('textarea');t.value=text;t.style.position='fixed';t.style.opacity='0';document.body.append(t);t.select();const ok=document.execCommand('copy');t.remove();toast(ok?'コピーしました。':'コピーできませんでした。本文を選択してコピーしてください。');}
  }
  $$('[data-copy-target]').forEach(b=>b.addEventListener('click',()=>{const target=document.getElementById(b.dataset.copyTarget);if(target)copyText('value'in target?target.value:target.textContent);}));
  $$('[data-copy-url]').forEach(b=>b.addEventListener('click',()=>{if(location.protocol==='file:'){toast('公開後のページでURLをコピーするか、付属のMarkdownを取り込んでください。');return;}copyText(location.href.split('#')[0]);}));
  $$('[data-print]').forEach(b=>b.addEventListener('click',()=>window.print()));
  $$('.quiz').forEach(el=>{
    const key=el.dataset.key, correct=Number(el.dataset.answer), feedback=$('.quiz-feedback',el), explanation=feedback?.dataset.explanation||'';
    function display(choice,announce=false){
      $$('.quiz-option',el).forEach(btn=>{const own=Number(btn.dataset.choice);btn.classList.toggle('correct',own===correct);btn.classList.toggle('wrong',own===choice&&choice!==correct);btn.setAttribute('aria-pressed',String(own===choice));});
      if(feedback){feedback.hidden=false;feedback.classList.toggle('error',choice!==correct);feedback.textContent=(choice===correct?'正解です。':'もう一度考えてみましょう。正解は '+['A','B','C'][correct]+' です。')+' '+explanation;}
      if(announce){state.quiz[key]={choice,correct:choice===correct};save();renderProgress();}
    }
    $$('.quiz-option',el).forEach(btn=>btn.addEventListener('click',()=>display(Number(btn.dataset.choice),true)));
    if(state.quiz[key])display(state.quiz[key].choice);
  });
  const search=$('#site-search'), results=$('#search-results');
  function escapeHTML(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  search?.addEventListener('input',()=>{
    const term=search.value.trim().toLocaleLowerCase('ja');
    if(!term){results.hidden=true;return;}
    const hits=(window.COURSE_SEARCH||[]).filter(x=>x.text.toLocaleLowerCase('ja').includes(term));
    results.replaceChildren();
    if(!hits.length){const p=document.createElement('p');p.className='search-empty';p.textContent='一致する章がありません。日本語・英語の別表記でも試してください。';results.append(p);}
    hits.forEach(hit=>{const a=document.createElement('a');a.className='search-result';a.href=lessonLink(hit.id);a.innerHTML=`<span class="mono">${String(hit.id).padStart(2,'0')}</span>　${escapeHTML(hit.title)}<small>${escapeHTML(hit.desc)}</small>`;a.addEventListener('click',()=>{results.hidden=true;search.value='';});results.append(a);});
    results.hidden=false;
  });
  document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeMenu();if(results)results.hidden=true;}if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'&&search){e.preventDefault();search.focus();}});
  document.addEventListener('click',e=>{if(results&&!results.contains(e.target)&&e.target!==search)results.hidden=true;});
  const glossarySearch=$('#glossary-search');glossarySearch?.addEventListener('input',()=>{const term=glossarySearch.value.toLowerCase().trim();let count=0;$$('.glossary-item').forEach(el=>{el.hidden=!el.textContent.toLowerCase().includes(term);if(!el.hidden)count++;});const out=$('#glossary-count');if(out)out.textContent=`${count}語を表示`;});
  function downloadBlob(text,name,type){const u=URL.createObjectURL(new Blob([text],{type}));const a=document.createElement('a');a.href=u;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),10000);}
  $$('[data-export-progress]').forEach(b=>b.addEventListener('click',()=>downloadBlob(JSON.stringify(state,null,2),'vla-learning-progress.json','application/json')));
  $('#import-progress')?.addEventListener('change',async e=>{const file=e.target.files?.[0];if(!file)return;try{if(file.size>2_000_000)throw new Error('ファイルが大きすぎます。');const imported=cleanState(JSON.parse(await file.text()));if(!confirm('現在の学習履歴とメモを、選んだファイルで置き換えますか？'))return;state=imported;save();location.reload();}catch(err){toast('読み込めません：'+err.message);}finally{e.target.value='';}});
  $$('[data-reset-progress]').forEach(b=>b.addEventListener('click',()=>{if(!confirm('このブラウザの学習履歴・クイズ・メモをすべて削除しますか？先に書き出して保存できます。'))return;state=defaults();save();location.reload();}));
  function renderReview(){const target=$('#review-list');if(!target)return;target.replaceChildren();const wrong=Object.entries(state.quiz).filter(([k,v])=>!v.correct);if(!wrong.length){const p=document.createElement('p');p.className='note';p.textContent=Object.keys(state.quiz).length?'記録されている不正解はありません。時間を置いて説明し直してみましょう。':'確認問題に答えると、間違えた章をここで振り返れます。';target.append(p);return;}const ids=[...new Set(wrong.map(([key])=>Number(key.split('-')[0])))];ids.forEach(id=>{const info=(window.COURSE_SEARCH||[]).find(x=>x.id===id);const a=document.createElement('a');a.className='review-item';a.href=document.body.dataset.standalone==='true'?`#quiz-${String(id).padStart(2,'0')}`:lessonLink(id)+'#quiz';a.textContent=`第${String(id).padStart(2,'0')}章　${info?.title||''}`;target.append(a);});}
  const selector=$('#prompt-lesson');if(selector){const update=()=>{const id=Number(selector.value), entry=(window.COURSE_PROMPTS||[]).find(x=>x.id===id);if(entry){$('#video-prompt').value=entry.text;const link=$('#selected-source');if(link)link.href=(document.body.dataset.prefix||'')+`notebooklm/chapters/${String(id).padStart(2,'0')}.md`;}};selector.addEventListener('change',update);update();}
  $$('.demo').forEach(demo=>{
    const kind=demo.dataset.demo;
    if(kind==='temperature'){
      const range=$('input',demo);const update=()=>{const t=Number(range.value);$('output',demo).value=t.toFixed(1);const logits=[3,1,0],m=Math.max(...logits),exp=logits.map(x=>Math.exp((x-m)/t)),sum=exp.reduce((a,b)=>a+b,0);$$('.probability-row',demo).forEach((row,i)=>{const percent=exp[i]/sum*100;$('.probability-bar',row).style.width=percent+'%';$('.probability-value',row).textContent=percent.toFixed(1)+'%';});};range.addEventListener('input',update);update();
    }
    if(kind==='lora'){
      const range=$('input',demo);const update=()=>{const r=Number(range.value),base=4096**2,extra=r*8192;$('output',demo).value=String(r);$('[data-base]',demo).textContent=base.toLocaleString();$('[data-extra]',demo).textContent=extra.toLocaleString();$('[data-ratio]',demo).textContent=(extra/base*100).toFixed(2)+'%';};range.addEventListener('input',update);update();
    }
    if(kind==='chunk'){
      const range=$('input',demo);const strip=$('.chunk-strip',demo);for(let i=1;i<=32;i++){const x=document.createElement('span');x.className='chunk-cell';x.textContent=String(i);strip.append(x);}const update=()=>{const k=Number(range.value);$('output',demo).value=String(k);$('[data-exec-time]',demo).textContent=(k/50).toFixed(2)+'秒';$('[data-budget]',demo).textContent=(k/50*1000-100).toFixed(0)+' ms';$$('.chunk-cell',demo).forEach((x,i)=>x.classList.toggle('execute',i<k));$('[data-chunk-status]',demo).textContent=k/50<.1?'仮定の100ms推論より実行区間が短い設定です。非同期でも計算が間に合うか確認が必要です。':'この単純計算では100msの推論を重ねる時間があります。ただし通信・揺らぎ・切替処理は含めていません。';};range.addEventListener('input',update);update();
    }
    if(kind==='gradient'){
      const rate=$('input',demo),history=$('.gradient-history',demo);let w=-2,steps=0;const render=()=>{$('output',demo).value=Number(rate.value).toFixed(2);$('[data-weight]',demo).textContent=Number.isFinite(w)?w.toFixed(4):'発散';$('[data-loss]',demo).textContent=Number.isFinite(w)?((w-2)**2).toFixed(4):'発散';};rate.addEventListener('input',render);$('[data-step]',demo).addEventListener('click',()=>{if(steps>=50||!Number.isFinite(w)||Math.abs(w)>1e8){toast('リセットして別の学習率を試してください。');return;}w-=Number(rate.value)*2*(w-2);steps++;const p=document.createElement('div');p.textContent=`${steps}回目：w=${w.toFixed(4)}, loss=${((w-2)**2).toFixed(4)}`;history.prepend(p);render();});$('[data-gradient-reset]',demo).addEventListener('click',()=>{w=-2;steps=0;history.replaceChildren();render();});render();
    }
  });
  const reading=$('.reading-progress');if(reading){const update=()=>{const max=document.documentElement.scrollHeight-window.innerHeight;reading.style.width=(max>0?window.scrollY/max:0)*(window.innerWidth-(window.innerWidth>760?(window.innerWidth>950?252:222):0))+'px';};window.addEventListener('scroll',update,{passive:true});window.addEventListener('resize',update);update();}
  if(!storageAvailable){const warning=$('#storage-warning');if(warning)warning.hidden=false;toast('この環境では学習履歴を読み込めません。保存できない場合は履歴を書き出して保管してください。');}
})();
