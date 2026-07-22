#!/usr/bin/env python3
"""Rebuild index.html from data/quotes.csv. Run:  python3 scripts/build.py"""
import json, csv, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV_PATH = os.path.join(ROOT, "data", "quotes.csv")
OUT_PATH = os.path.join(ROOT, "index.html")

with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))
quotes = [{"q": r["Quote"], "a": r.get("Author", "") or "", "s": r.get("Source", "") or "",
           "t": r.get("Theme", "") or ""} for r in rows if (r.get("Quote") or "").strip()]
themes = sorted(set(q["t"] for q in quotes if q["t"]))
payload = json.dumps(quotes, ensure_ascii=False).replace("</", "<\\/")
themes_json = json.dumps(themes, ensure_ascii=False)

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Quote Engine</title>
<style>
  :root{
    --bg:#f4f1ea; --card:#fffdf8; --ink:#1f1b16; --muted:#7c7264; --line:#e6dfd2;
    --accent:#b4531f; --danger:#a23b2c; --shadow:0 18px 50px -20px rgba(60,40,20,.35);
  }
  html[data-mode="dark"]{
    --bg:#14110d; --card:#1e1a15; --ink:#efe9df; --muted:#9c9184; --line:#332d25;
    --accent:#e08a4c; --danger:#e0765f; --shadow:0 24px 60px -24px rgba(0,0,0,.7);
  }
  *{box-sizing:border-box}
  html,body{height:100%}
  body{
    margin:0; background:radial-gradient(circle at 50% -10%, color-mix(in srgb,var(--accent) 8%, var(--bg)), var(--bg) 60%);
    color:var(--ink); font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    padding:64px 18px 52px; height:100vh; overflow:hidden; transition:background .4s,color .4s;
  }
  .topbar{position:fixed; top:14px; left:0; right:0; display:flex; gap:10px; justify-content:space-between;
    align-items:center; padding:0 18px; max-width:940px; margin:0 auto; width:100%; z-index:5;}
  .tb-right{display:flex; gap:8px}
  select,.iconbtn{
    font:inherit; font-size:14px; color:var(--ink); background:var(--card); border:1px solid var(--line);
    border-radius:999px; padding:8px 14px; cursor:pointer; -webkit-appearance:none; appearance:none;
  }
  select{padding-right:30px; max-width:52vw; text-overflow:ellipsis;
    background-image:linear-gradient(45deg,transparent 50%,var(--muted) 50%),linear-gradient(135deg,var(--muted) 50%,transparent 50%);
    background-position:calc(100% - 16px) 55%,calc(100% - 11px) 55%; background-size:5px 5px,5px 5px; background-repeat:no-repeat;}
  .iconbtn{font-family:system-ui,sans-serif}
  .iconbtn:hover{border-color:var(--accent)}
  .card{
    background:var(--card); border:1px solid var(--line); border-radius:22px; box-shadow:var(--shadow);
    max-width:760px; width:100%; padding:clamp(24px,4vw,52px); position:relative; overflow:hidden;
    max-height:calc(100vh - 132px); display:flex; flex-direction:column;
  }
  .card::before{content:"\201C"; position:absolute; top:-18px; left:18px; font-size:150px; line-height:1;
    color:var(--accent); opacity:.14; font-family:Georgia,serif; pointer-events:none;}
  .theme{flex:0 0 auto; align-self:flex-start; font-family:system-ui,sans-serif; font-size:12px; letter-spacing:.08em;
    text-transform:uppercase; font-weight:600; color:var(--accent);
    background:color-mix(in srgb,var(--accent) 12%, transparent); border:1px solid color-mix(in srgb,var(--accent) 25%, transparent);
    padding:5px 12px; border-radius:999px; margin-bottom:20px;}
  .quote{flex:1 1 auto; min-height:0; overflow:auto; font-size:28px; line-height:1.5; font-weight:500; margin:0 0 22px;}
  .meta{flex:0 0 auto; border-top:1px solid var(--line); padding-top:16px; display:flex; flex-direction:column; gap:3px}
  .author{font-weight:700; font-size:18px}
  .source{color:var(--muted); font-size:15px; font-style:italic}
  .controls{flex:0 0 auto; display:flex; gap:12px; align-items:center; margin-top:22px; flex-wrap:wrap; justify-content:center}
  .refresh{
    font-family:system-ui,sans-serif; font-size:16px; font-weight:600; color:#fff; background:var(--accent);
    border:none; border-radius:999px; padding:14px 30px; cursor:pointer; box-shadow:0 8px 20px -8px var(--accent);
    transition:transform .08s ease, filter .2s;
  }
  .refresh:hover{filter:brightness(1.06)} .refresh:active{transform:translateY(1px) scale(.99)}
  .prefs{flex:0 0 auto; display:flex; gap:9px; align-items:center; justify-content:center; margin-top:14px; flex-wrap:wrap}
  .pref{font-family:system-ui,sans-serif; font-size:13px; font-weight:600; color:var(--muted);
    background:transparent; border:1px solid var(--line); border-radius:999px; padding:8px 14px; cursor:pointer;
    transition:color .15s,border-color .15s,background .15s;}
  .pref:hover{color:var(--ink); border-color:var(--accent)}
  #more:hover{color:var(--accent)}
  .pref.danger:hover{color:var(--danger); border-color:var(--danger)}
  .freq{font-family:system-ui,sans-serif; font-size:12px; font-weight:700; letter-spacing:.03em;
    min-width:78px; text-align:center; padding:6px 10px; border-radius:999px; transition:transform .16s;
    background:color-mix(in srgb,var(--muted) 14%, transparent); color:var(--muted)}
  .freq[data-level="o"]{background:color-mix(in srgb,var(--accent) 22%, transparent); color:var(--accent)}
  .freq[data-level="m"]{background:color-mix(in srgb,var(--accent) 13%, transparent); color:var(--accent)}
  .freq[data-level="l"]{background:color-mix(in srgb,#5f7a52 16%, transparent); color:#5f7a52}
  .freq[data-level="r"]{background:color-mix(in srgb,#8a8f98 20%, transparent); color:#8a8f98; text-decoration:line-through}
  html[data-mode="dark"] .freq[data-level="l"]{color:#9fc38c}
  .count{font-family:system-ui,sans-serif; font-size:13px; color:var(--muted); margin-top:16px; text-align:center}
  .resetlink{color:var(--muted); text-decoration:underline; cursor:pointer}
  .resetlink:hover{color:var(--accent)}

  /* toast */
  .toast{position:fixed; bottom:22px; left:50%; transform:translateX(-50%) translateY(20px);
    background:var(--ink); color:var(--bg); font-family:system-ui,sans-serif; font-size:14px; font-weight:500;
    padding:11px 18px; border-radius:999px; box-shadow:var(--shadow); opacity:0; pointer-events:none;
    transition:opacity .25s, transform .25s; z-index:40; display:flex; gap:14px; align-items:center;}
  .toast.show{opacity:1; transform:translateX(-50%) translateY(0); pointer-events:auto}
  .toast .undo{color:var(--accent); font-weight:700; cursor:pointer; text-decoration:underline}
  html[data-mode="dark"] .toast{background:#efe9df; color:#14110d}

  /* drawer */
  .overlay{position:fixed; inset:0; background:rgba(20,14,8,.42); opacity:0; pointer-events:none;
    transition:opacity .25s; z-index:20;}
  .overlay.open{opacity:1; pointer-events:auto}
  .drawer{position:fixed; top:0; right:0; height:100%; width:min(430px,92vw); background:var(--card);
    border-left:1px solid var(--line); box-shadow:var(--shadow); transform:translateX(102%);
    transition:transform .3s ease; z-index:30; display:flex; flex-direction:column;}
  .drawer.open{transform:none}
  .drawer-inner{padding:20px 22px 30px; overflow:auto; font-family:system-ui,sans-serif}
  .drawer-head{display:flex; justify-content:space-between; align-items:center; margin-bottom:6px}
  .drawer-head b{font-size:18px}
  .sec{border-top:1px solid var(--line); padding:18px 0 4px; margin-top:8px}
  .sec h3{font-size:13px; letter-spacing:.05em; text-transform:uppercase; color:var(--accent); margin:0 0 12px}
  label{display:block; font-size:12px; color:var(--muted); margin:10px 0 4px; font-weight:600}
  .fld{width:100%; font:inherit; font-size:14px; color:var(--ink); background:var(--bg); border:1px solid var(--line);
    border-radius:12px; padding:10px 12px;}
  textarea.fld{min-height:96px; resize:vertical; font-family:inherit}
  .btnrow{display:flex; gap:10px; flex-wrap:wrap; margin-top:14px}
  .btn{font:inherit; font-size:14px; font-weight:600; border-radius:999px; padding:10px 18px; cursor:pointer;
    border:1px solid var(--line); background:transparent; color:var(--ink)}
  .btn:hover{border-color:var(--accent)}
  .btn.primary{background:var(--accent); color:#fff; border-color:var(--accent)}
  .btn.primary:hover{filter:brightness(1.06)}
  .btn.ghost{color:var(--muted)}
  .note{font-size:12px; color:var(--muted); margin:8px 0 0; line-height:1.5}
  .result{font-size:13px; color:var(--accent); margin-top:8px; min-height:16px}
  input[type=file]{font-size:13px; color:var(--muted)}
  input[type=file]::file-selector-button{font:inherit; font-weight:600; margin-right:10px; cursor:pointer;
    border:1px solid var(--line); background:var(--bg); color:var(--ink); border-radius:999px; padding:7px 14px;}
  .card,.drawer{animation:none}
  .card.anim{animation:fade .45s ease} @keyframes fade{from{opacity:0; transform:translateY(8px)} to{opacity:1; transform:none}}
  .hint{font-family:system-ui,sans-serif; font-size:12px; color:var(--muted)}
  .empty{font-size:20px; color:var(--muted); text-align:center; padding:20px 0}
</style>
</head>
<body>
  <div class="topbar">
    <select id="filter" title="Filter by theme"><option value="__all">All themes</option></select>
    <div class="tb-right">
      <button class="iconbtn" id="manage" title="Add, import, export, manage">☰ Manage</button>
      <button class="iconbtn" id="mode" title="Toggle light/dark">◐ Theme</button>
    </div>
  </div>

  <div class="card anim" id="card">
    <span class="theme" id="qtheme"></span>
    <blockquote class="quote" id="qtext"></blockquote>
    <div class="meta">
      <span class="author" id="qauthor"></span>
      <span class="source" id="qsource"></span>
    </div>
    <div class="controls">
      <button class="refresh" id="refresh">↻ New quote</button>
      <span class="hint">or press <b>Space</b></span>
    </div>
    <div class="prefs">
      <button class="pref" id="less" title="Show less often (↓)">▼ Less</button>
      <span class="freq" id="freq" data-level="n">Normal</span>
      <button class="pref" id="more" title="Show more often (↑)">More ▲</button>
      <button class="pref" id="edit" title="Edit this quote">✎ Edit</button>
      <button class="pref danger" id="del" title="Never show this quote again">🗑 Never show</button>
    </div>
  </div>
  <div class="count"><span id="count"></span> · <a class="resetlink" id="reset">reset weights</a></div>

  <div class="toast" id="toast"></div>
  <div class="overlay" id="overlay"></div>

  <div class="drawer" id="drawer">
    <div class="drawer-inner">
      <div class="drawer-head"><b>Manage quotes</b><button class="iconbtn" id="closeDrawer">✕</button></div>

      <div class="sec">
        <h3 id="formTitle">Add a quote</h3>
        <label>Theme</label>
        <select class="fld" id="fTheme"></select>
        <div id="fNewWrap" style="display:none">
          <label>New theme name</label>
          <input class="fld" id="fNewTheme" placeholder="e.g. Courage in Adversity">
        </div>
        <label>Author</label>
        <input class="fld" id="fAuthor" placeholder="e.g. Marcus Aurelius, or @handle">
        <label>Source</label>
        <input class="fld" id="fSource" placeholder="e.g. Meditations, or X">
        <label>Quote</label>
        <textarea class="fld" id="fQuote" placeholder="Paste the quote text…"></textarea>
        <div class="btnrow">
          <button class="btn primary" id="saveQuote">Save quote</button>
          <button class="btn ghost" id="cancelEdit" style="display:none">Cancel edit</button>
        </div>
        <div class="result" id="formResult"></div>
      </div>

      <div class="sec">
        <h3>Import quotes from CSV</h3>
        <p class="note">Pick a CSV with columns <b>Quote, Author, Source, Theme</b> (same as your master file). New quotes are appended; duplicates are skipped.</p>
        <input type="file" id="importCsv" accept=".csv,text/csv">
        <div class="result" id="importCsvResult"></div>
      </div>

      <div class="sec">
        <h3>Backup &amp; move between devices</h3>
        <p class="note">Preferences = your frequency weights + added quotes + hidden quotes. Export it to carry your setup to another computer.</p>
        <div class="btnrow">
          <button class="btn" id="exportPrefs">⭳ Export preferences</button>
          <label class="btn" style="margin:0" for="importPrefs">⭱ Import preferences</label>
          <input type="file" id="importPrefs" accept=".json,application/json" style="display:none">
        </div>
        <p class="note" style="margin-top:14px">Or export the full quote list (with your edits) as CSV to refresh your Google Sheet:</p>
        <div class="btnrow">
          <button class="btn" id="exportCsv">⭳ Export quotes (CSV)</button>
        </div>
        <div class="result" id="prefsResult"></div>
      </div>

      <div class="sec">
        <h3>Hidden quotes</h3>
        <p class="note"><span id="hiddenCount">0</span> quote(s) hidden. <a class="resetlink" id="restoreAll">Restore all</a></p>
      </div>
    </div>
  </div>

<script>
const QUOTES = __PAYLOAD__;
let THEMES = __THEMES__;
QUOTES.forEach((q,i)=>q.id=i);
const el = id => document.getElementById(id);

// ---------- persisted state ----------
const PKEY='quoteEngine.prefs.v1';
let weights={}, deleted=new Set(), CUSTOM=[], nextCustomId=1;
function loadPrefs(){
  try{ const raw=localStorage.getItem(PKEY);
    if(raw){ const o=JSON.parse(raw)||{};
      weights=o.weights||{}; deleted=new Set((o.deleted||[]).map(String));
      CUSTOM=Array.isArray(o.custom)?o.custom:[]; nextCustomId=o.nextCustomId||1; return; } }catch(e){}
  try{ const old=localStorage.getItem('quoteEngine.weights.v1'); if(old) weights=JSON.parse(old)||{}; }catch(e){}
}
function savePrefs(){ try{ localStorage.setItem(PKEY, JSON.stringify(
  {v:2, weights, deleted:[...deleted], custom:CUSTOM, nextCustomId})); }catch(e){} }
loadPrefs();

const qid = q => String(q.id);
const W = q => { const w=weights[qid(q)]; return w==null?1:w; };
const MOREF=1.7, LESSF=0.58, WMAX=12, WMIN=0.06;

function activeQuotes(){ return QUOTES.concat(CUSTOM).filter(q=>!deleted.has(qid(q))); }
function allThemes(){
  const set=new Set(THEMES);
  CUSTOM.forEach(q=>{ if(!deleted.has(qid(q))) set.add(q.t); });
  // keep base order, then any new themes alphabetically
  const extra=[...set].filter(t=>!THEMES.includes(t)).sort();
  return THEMES.concat(extra);
}

let pool=[], current=null;

// ---------- theme selects ----------
function refreshThemes(){
  const list=allThemes();
  const fv=el('filter').value;
  el('filter').innerHTML='<option value="__all">All themes</option>'+
    list.map(t=>'<option>'+esc(t)+'</option>').join('');
  el('filter').value=list.includes(fv)||fv==='__all'?fv:'__all';
  const tv=el('fTheme').value;
  el('fTheme').innerHTML=list.map(t=>'<option>'+esc(t)+'</option>').join('')+
    '<option value="__new">➕ New theme…</option>';
  if(tv) el('fTheme').value=tv;
}
function esc(s){ return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

// ---------- fit ----------
function fitQuote(){
  const qt=el('qtext'); qt.style.overflow='hidden';
  let size=Math.min(30, Math.max(19, window.innerWidth*0.03));
  const setLH=s=>qt.style.lineHeight=s<17?1.34:(s<20?1.42:1.5);
  qt.style.fontSize=size+'px'; setLH(size);
  let guard=0;
  while(qt.scrollHeight>qt.clientHeight+1 && size>12 && guard<90){ size-=1; qt.style.fontSize=size+'px'; setLH(size); guard++; }
  qt.style.overflow=(qt.scrollHeight>qt.clientHeight+1)?'auto':'hidden';
}
let _rt; window.addEventListener('resize', ()=>{ clearTimeout(_rt); _rt=setTimeout(fitQuote,120); });

// ---------- selection ----------
function weightedPick(){
  if(pool.length===1) return pool[0];
  let total=0; for(const q of pool){ let w=W(q); if(q===current) w*=0.02; total+=w; }
  let r=Math.random()*total;
  for(const q of pool){ let w=W(q); if(q===current) w*=0.02; r-=w; if(r<=0) return q; }
  return pool[pool.length-1];
}
function freqInfo(w){
  if(w<=0.2) return ['Rarely','r']; if(w<=0.62) return ['Less often','l'];
  if(w<1.7) return ['Normal','n']; if(w<4) return ['More often','m']; return ['Often','o'];
}
function renderFreq(){ if(!current) return; const [lab,lvl]=freqInfo(W(current)); const f=el('freq'); f.textContent=lab; f.dataset.level=lvl; }
function setCardEnabled(on){ ['more','less','edit','del'].forEach(id=>el(id).disabled=!on); }

function show(){
  if(!pool.length){ current=null;
    el('qtheme').textContent=''; el('qtext').innerHTML='<div class="empty">No quotes in this view.<br>Try another theme or restore hidden quotes.</div>';
    el('qauthor').textContent=''; el('qsource').textContent=''; el('freq').textContent='—'; setCardEnabled(false); return; }
  setCardEnabled(true);
  current=weightedPick();
  el('qtheme').textContent=current.t;
  el('qtext').textContent='“'+current.q+'”';
  el('qauthor').textContent=current.a;
  el('qsource').textContent=current.s==='X'?'via X':current.s;
  renderFreq();
  const card=el('card'); card.classList.remove('anim'); void card.offsetWidth; card.classList.add('anim');
  fitQuote();
}
function adjust(factor){
  if(!current) return;
  let w=W(current)*factor; w=Math.max(WMIN,Math.min(WMAX,w));
  if(Math.abs(w-1)<0.04) delete weights[qid(current)]; else weights[qid(current)]=+w.toFixed(3);
  savePrefs(); renderFreq();
  const f=el('freq'); f.style.transform='scale(1.14)'; setTimeout(()=>f.style.transform='',160);
}
function applyFilter(){
  const v=el('filter').value;
  const base=activeQuotes();
  pool=(v==='__all')?base:base.filter(q=>q.t===v);
  el('count').textContent=pool.length+' quotes'+(v==='__all'?' · '+allThemes().length+' themes':' in this theme');
  el('hiddenCount').textContent=deleted.size;
  current=null; show();
}

// ---------- toast ----------
function toast(msg, undoFn){
  const t=el('toast'); t.innerHTML=''; const s=document.createElement('span'); s.textContent=msg; t.appendChild(s);
  if(undoFn){ const a=document.createElement('a'); a.className='undo'; a.textContent='Undo';
    a.onclick=()=>{ undoFn(); t.classList.remove('show'); }; t.appendChild(a); }
  t.classList.add('show'); clearTimeout(t._t); t._t=setTimeout(()=>t.classList.remove('show'),4500);
}

// ---------- delete ----------
function delCurrent(){
  if(!current) return; const id=qid(current);
  deleted.add(id); savePrefs(); applyFilter();
  toast('Quote hidden.', ()=>{ deleted.delete(id); savePrefs(); applyFilter(); });
}

// ---------- add / edit ----------
let editingId=null;
function openDrawer(){ el('drawer').classList.add('open'); el('overlay').classList.add('open'); }
function closeDrawer(){ el('drawer').classList.remove('open'); el('overlay').classList.remove('open'); }
function resetForm(){
  editingId=null; el('formTitle').textContent='Add a quote';
  el('fAuthor').value=''; el('fSource').value=''; el('fQuote').value='';
  el('fNewTheme').value=''; el('fNewWrap').style.display='none';
  el('fTheme').value=allThemes()[0]; el('cancelEdit').style.display='none'; el('formResult').textContent='';
}
function loadIntoForm(q){
  editingId=q.id; el('formTitle').textContent='Editing quote';
  refreshThemes();
  if(allThemes().includes(q.t)){ el('fTheme').value=q.t; el('fNewWrap').style.display='none'; }
  el('fAuthor').value=q.a||''; el('fSource').value=q.s||''; el('fQuote').value=q.q||'';
  el('cancelEdit').style.display=''; el('formResult').textContent='';
}
function themeFromForm(){
  const v=el('fTheme').value;
  return v==='__new' ? el('fNewTheme').value.trim() : v;
}
function saveQuote(){
  const q=el('fQuote').value.trim(), t=themeFromForm();
  const a=el('fAuthor').value.trim(), s=el('fSource').value.trim();
  if(!q){ el('formResult').textContent='Please enter the quote text.'; return; }
  if(!t){ el('formResult').textContent='Please choose or name a theme.'; return; }
  if(editingId!=null){
    const cust=CUSTOM.find(c=>String(c.id)===String(editingId));
    if(cust){ cust.q=q; cust.a=a; cust.s=s||'—'; cust.t=t; }
    else { // built-in: hide original, add replacement carrying its weight
      const w=weights[String(editingId)];
      deleted.add(String(editingId));
      const id='c'+(nextCustomId++); CUSTOM.push({id,q,a,s:s||'—',t});
      if(w!=null) weights[id]=w;
    }
    savePrefs(); refreshThemes(); applyFilter(); toast('Quote updated.'); resetForm();
  } else {
    const id='c'+(nextCustomId++); CUSTOM.push({id,q,a,s:s||'—',t});
    savePrefs(); refreshThemes(); applyFilter(); toast('Quote added.');
    el('fQuote').value=''; el('formResult').textContent='Added ✓ — add another or close.';
  }
}

// ---------- CSV ----------
function parseCSV(text){
  text=text.replace(/^﻿/,''); const rows=[]; let i=0,f='',row=[],inq=false;
  while(i<text.length){ const c=text[i];
    if(inq){ if(c==='"'){ if(text[i+1]==='"'){f+='"';i+=2;continue;} inq=false;i++;continue; } f+=c;i++; }
    else { if(c==='"'){inq=true;i++;} else if(c===','){row.push(f);f='';i++;}
      else if(c==='\r'){i++;} else if(c==='\n'){row.push(f);rows.push(row);row=[];f='';i++;}
      else {f+=c;i++;} } }
  if(f.length||row.length){ row.push(f); rows.push(row); }
  return rows;
}
function importCSV(text){
  const rows=parseCSV(text).filter(r=>r.length && r.some(c=>c.trim()!==''));
  if(!rows.length){ el('importCsvResult').textContent='No rows found.'; return; }
  const head=rows[0].map(h=>h.trim().toLowerCase());
  const iQ=head.findIndex(h=>h.includes('quote')), iA=head.findIndex(h=>h.includes('author')),
        iS=head.findIndex(h=>h.includes('source')), iT=head.findIndex(h=>h.includes('theme'));
  if(iQ<0||iT<0){ el('importCsvResult').textContent='Need at least Quote and Theme columns.'; return; }
  const norm=s=>s.toLowerCase().replace(/[^a-z0-9]/g,'');
  const seen=new Set(activeQuotes().map(q=>norm(q.q)));
  let added=0,skipped=0;
  for(let r=1;r<rows.length;r++){
    const row=rows[r]; const q=(row[iQ]||'').trim(); if(!q) continue;
    const key=norm(q); if(seen.has(key)){ skipped++; continue; }
    seen.add(key);
    CUSTOM.push({id:'c'+(nextCustomId++), q, a:(iA>=0?row[iA]:'').trim()||'—',
      s:(iS>=0?row[iS]:'').trim()||'—', t:(row[iT]||'').trim()||'Uncategorized'});
    added++;
  }
  savePrefs(); refreshThemes(); applyFilter();
  el('importCsvResult').textContent='Added '+added+' quote(s)'+(skipped?', skipped '+skipped+' duplicate(s).':'.');
}

// ---------- downloads ----------
function download(name, text, type){
  const blob=new Blob([text],{type}); const url=URL.createObjectURL(blob);
  const a=document.createElement('a'); a.href=url; a.download=name; document.body.appendChild(a); a.click();
  a.remove(); setTimeout(()=>URL.revokeObjectURL(url),1500);
}
function csvCell(s){ s=String(s==null?'':s); return /[",\n\r]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s; }
function exportCSV(){
  const list=activeQuotes(); const lines=['Quote,Author,Source,Theme'];
  for(const q of list) lines.push([q.q,q.a,q.s,q.t].map(csvCell).join(','));
  download('quotes.csv','﻿'+lines.join('\r\n'),'text/csv;charset=utf-8');
  el('prefsResult').textContent='Exported '+list.length+' quotes.';
}
function exportPrefs(){
  download('quote-engine-prefs.json', JSON.stringify({v:2,weights,deleted:[...deleted],custom:CUSTOM,nextCustomId}),
    'application/json');
  el('prefsResult').textContent='Preferences exported.';
}
function importPrefsObj(o){
  if(!o||typeof o!=='object'){ el('prefsResult').textContent='Invalid file.'; return; }
  if(o.weights) Object.assign(weights,o.weights);
  if(Array.isArray(o.deleted)) o.deleted.forEach(d=>deleted.add(String(d)));
  if(Array.isArray(o.custom)){ const have=new Set(CUSTOM.map(c=>String(c.id)));
    o.custom.forEach(c=>{ if(!have.has(String(c.id))) CUSTOM.push(c); }); }
  if(o.nextCustomId) nextCustomId=Math.max(nextCustomId,o.nextCustomId);
  savePrefs(); refreshThemes(); applyFilter();
  el('prefsResult').textContent='Preferences imported.';
}
function readFile(input, cb){
  const f=input.files[0]; if(!f) return; const r=new FileReader();
  r.onload=()=>{ cb(r.result); input.value=''; }; r.readAsText(f);
}

// ---------- events ----------
el('refresh').addEventListener('click', show);
el('more').addEventListener('click', ()=>adjust(MOREF));
el('less').addEventListener('click', ()=>adjust(LESSF));
el('edit').addEventListener('click', ()=>{ if(current){ loadIntoForm(current); openDrawer(); } });
el('del').addEventListener('click', delCurrent);
el('filter').addEventListener('change', applyFilter);
el('mode').addEventListener('click', ()=>{ const h=document.documentElement; h.dataset.mode=h.dataset.mode==='dark'?'light':'dark'; });
el('reset').addEventListener('click', ()=>{ weights={}; savePrefs(); renderFreq(); toast('Frequency weights reset.'); });

el('manage').addEventListener('click', ()=>{ resetForm(); openDrawer(); });
el('closeDrawer').addEventListener('click', closeDrawer);
el('overlay').addEventListener('click', closeDrawer);
el('fTheme').addEventListener('change', e=>{ el('fNewWrap').style.display = e.target.value==='__new'?'':'none'; });
el('saveQuote').addEventListener('click', saveQuote);
el('cancelEdit').addEventListener('click', resetForm);
el('importCsv').addEventListener('change', e=>readFile(e.target, importCSV));
el('exportPrefs').addEventListener('click', exportPrefs);
el('exportCsv').addEventListener('click', exportCSV);
el('importPrefs').addEventListener('change', e=>readFile(e.target, txt=>{ try{ importPrefsObj(JSON.parse(txt)); }catch(err){ el('prefsResult').textContent='Could not read that file.'; } }));
el('restoreAll').addEventListener('click', ()=>{ deleted.clear(); savePrefs(); refreshThemes(); applyFilter(); toast('Hidden quotes restored.'); });

document.addEventListener('keydown', e=>{
  if(/^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName)) return;
  if(el('drawer').classList.contains('open')){ if(e.code==='Escape') closeDrawer(); return; }
  if(e.code==='Space'){ e.preventDefault(); show(); }
  else if(e.code==='ArrowUp'){ e.preventDefault(); adjust(MOREF); }
  else if(e.code==='ArrowDown'){ e.preventDefault(); adjust(LESSF); }
});

refreshThemes();
applyFilter();
</script>
</body>
</html>"""

out = TEMPLATE.replace("__PAYLOAD__", payload).replace("__THEMES__", themes_json)
with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(out)
print("Wrote", OUT_PATH, "-", len(out), "bytes;", len(quotes), "quotes;", len(themes), "themes")
