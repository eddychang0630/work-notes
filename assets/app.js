(() => {
  'use strict';
  const MERMAID_SRC = 'https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js';
  const app = document.getElementById('app');
  const titleEl = document.getElementById('title');
  const backBtn = document.getElementById('back');
  const topBtn = document.getElementById('top');
  const fontBtn = document.getElementById('font');

  let IDX = null;
  const TXT = {};
  const store = {
    get(k, d) { try { const v = JSON.parse(localStorage.getItem(k)); return v ?? d; } catch { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* private mode */ } }
  };
  const read = new Set(store.get('kb.read', []));
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const catOf = id => IDX.categories.find(c => c.id === id);
  const docsOf = id => IDX.docs.filter(d => d.cat === id);
  const pct = (a, b) => b ? Math.round(a / b * 100) : 0;

  async function getText(d) {
    if (!TXT[d.id]) {
      const r = await fetch(d.file);
      if (!r.ok) throw new Error('HTTP ' + r.status);
      TXT[d.id] = await r.text();
    }
    return TXT[d.id];
  }

  /* ---------- font size ---------- */
  const SIZES = [15, 16, 17.5, 19];
  let fs = store.get('kb.fs', 1);
  const applyFs = () => { document.documentElement.style.fontSize = SIZES[fs] + 'px'; };
  applyFs();
  fontBtn.onclick = () => { fs = (fs + 1) % SIZES.length; store.set('kb.fs', fs); applyFs(); };

  /* ---------- chrome ---------- */
  function chrome(title, tab, back) {
    titleEl.textContent = title;
    document.title = title === IDX.title ? title : title + '｜' + IDX.title;
    backBtn.hidden = !back;
    backBtn.onclick = () => { location.hash = back; };
    document.querySelectorAll('.tabbar a').forEach(a => a.classList.toggle('on', a.dataset.tab === tab));
    window.scrollTo(0, 0);
  }
  window.addEventListener('scroll', () => { topBtn.hidden = window.scrollY < 700; }, { passive: true });
  topBtn.onclick = () => window.scrollTo({ top: 0, behavior: 'smooth' });

  const card = d => {
    const done = read.has(d.id);
    return `<a class="doc ${done ? 'done' : ''}" href="#/doc/${d.id}">
      <span class="no">${esc(d.no || catOf(d.cat).icon)}</span>
      <span class="dt"><b>${esc(d.title)}</b><small>${esc(d.summary || '')}</small></span>
      <span class="chk">${done ? '✓' : '›'}</span></a>`;
  };

  /* ---------- views ---------- */
  function home() {
    chrome(IDX.title, 'home', null);
    const total = IDX.docs.length, done = IDX.docs.filter(d => read.has(d.id)).length;
    const last = IDX.docs.find(d => d.id === store.get('kb.last', null));
    const next = IDX.docs.find(d => !read.has(d.id));
    const go = last && !read.has(last.id) ? last : next;
    app.innerHTML = `
      <section class="hero">
        <h2>${esc(IDX.title)}</h2>
        <p>${esc(IDX.subtitle)}</p>
        <div class="bar"><i style="width:${pct(done, total)}%"></i></div>
        <div class="row"><span>已複習 ${done} / ${total} 篇</span><span>${pct(done, total)}%</span></div>
        ${go ? `<a class="go" href="#/doc/${go.id}">▶ 繼續閱讀：${esc((go.no ? go.no + ' ' : '') + go.title)}</a>` : '<span class="go">🎉 全部複習完成！</span>'}
      </section>
      <h2 class="sec">知識分類</h2>
      <div class="grid">${IDX.categories.map(c => {
        const ds = docsOf(c.id), dn = ds.filter(d => read.has(d.id)).length;
        return `<a class="cat" href="#/cat/${c.id}"><span class="ico">${c.icon}</span><b>${esc(c.title)}</b>
          <small>${esc(c.desc)}</small><div class="bar"><i style="width:${pct(dn, ds.length)}%"></i></div>
          <div class="meta"><span>${ds.length} 篇</span><span>${dn}/${ds.length}</span></div></a>`;
      }).join('')}</div>
      <h2 class="sec">最近新增</h2>
      <div class="list">${[...IDX.docs].filter(d => d.added).sort((a, b) => b.added.localeCompare(a.added)).slice(0, 4).map(card).join('')}</div>`;
  }

  function category(id) {
    const c = catOf(id);
    if (!c) return home();
    chrome(c.title, id === 'review' ? 'review' : 'home', '#/');
    app.innerHTML = `<div class="cathead"><span class="ico">${c.icon}</span><p>${esc(c.desc)}</p></div>
      <div class="list">${docsOf(id).map(card).join('') || '<p class="empty">這個分類還沒有內容</p>'}</div>`;
  }

  function path() {
    chrome('學習路徑', 'path', null);
    app.innerHTML = IDX.stages.map(s => `<p class="stage">${esc(s.title)}<small>${esc(s.desc)}</small></p>
      <div class="list" style="margin-bottom:22px">${s.docs.map(id => IDX.docs.find(d => d.id === id)).filter(Boolean).map(card).join('')}</div>`).join('');
  }

  function search() {
    chrome('搜尋', 'search', null);
    app.innerHTML = `<input class="searchbox" type="search" placeholder="搜尋全部筆記，例如：Linear11、401、0x68" autocomplete="off">
      <div id="hits" class="list" style="margin-top:12px"><p class="empty">輸入關鍵字開始搜尋</p></div>`;
    const box = app.querySelector('.searchbox'), hits = app.querySelector('#hits');
    const ready = Promise.all(IDX.docs.map(d => getText(d).catch(() => '')));
    let t;
    const run = async () => {
      const q = box.value.trim();
      store.set('kb.q', q);
      if (!q) { hits.innerHTML = '<p class="empty">輸入關鍵字開始搜尋</p>'; return; }
      await ready;
      const ql = q.toLowerCase(), out = [];
      for (const d of IDX.docs) {
        const txt = TXT[d.id] || '', low = txt.toLowerCase();
        const inTitle = d.title.toLowerCase().includes(ql);
        let i = low.indexOf(ql), n = 0, snip = '';
        if (i >= 0) {
          const a = Math.max(0, i - 30), raw = txt.slice(a, i + q.length + 60).replace(/\s+/g, ' ');
          snip = esc(raw).replace(new RegExp(esc(q).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'), m => `<mark>${m}</mark>`);
          while (i >= 0) { n++; i = low.indexOf(ql, i + ql.length); }
        }
        if (n || inTitle) out.push({ d, n, snip, score: n + (inTitle ? 100 : 0) });
      }
      out.sort((a, b) => b.score - a.score);
      hits.innerHTML = out.length ? out.map(o => `<a class="hit" href="#/doc/${o.d.id}">
        <b>${esc((o.d.no ? o.d.no + ' ' : '') + o.d.title)}</b>
        <small>${catOf(o.d.cat).icon} ${esc(catOf(o.d.cat).title)}・出現 ${o.n} 次</small>
        ${o.snip ? `<small>…${o.snip}…</small>` : ''}</a>`).join('') : '<p class="empty">找不到相關內容</p>';
    };
    box.addEventListener('input', () => { clearTimeout(t); t = setTimeout(run, 180); });
    box.value = store.get('kb.q', '');
    if (box.value) run();
  }

  async function doc(id) {
    const d = IDX.docs.find(x => x.id === id);
    if (!d) return home();
    const c = catOf(d.cat);
    chrome((d.no ? d.no + ' ' : '') + d.title, d.cat === 'review' ? 'review' : 'home', '#/cat/' + d.cat);
    app.innerHTML = '<p class="loading">載入中…</p>';
    let md;
    try { md = await getText(d); }
    catch (e) { app.innerHTML = `<p class="empty">內容載入失敗（${esc(e.message)}）。<br>若是直接開啟檔案，請改用本機伺服器或 GitHub Pages 網址。</p>`; return; }
    if (location.hash !== '#/doc/' + id) return;
    store.set('kb.last', id);

    const i = IDX.docs.indexOf(d), prev = IDX.docs[i - 1], next = IDX.docs[i + 1];
    app.innerHTML = `
      <div class="chips"><span class="chip">${c.icon} ${esc(c.title)}</span>${d.level ? `<span class="chip">${esc(d.level)}</span>` : ''}${(d.tags || []).map(t => `<span class="chip">${esc(t)}</span>`).join('')}</div>
      <details class="toc"><summary>📑 本篇目錄</summary><ol></ol></details>
      <article class="md">${window.marked.parse(md)}</article>
      <button class="donebtn"></button>
      <div class="pn">
        ${prev ? `<a href="#/doc/${prev.id}"><small>‹ 上一篇</small>${esc(prev.title)}</a>` : '<span style="flex:1"></span>'}
        ${next ? `<a class="next" href="#/doc/${next.id}"><small>下一篇 ›</small>${esc(next.title)}</a>` : '<span style="flex:1"></span>'}
      </div>`;
    const art = app.querySelector('article');

    // callouts
    const kinds = [['⚠️', 'warn'], ['💡', 'tip'], ['🔴', 'danger'], ['✅', 'ok'], ['📌', 'note']];
    art.querySelectorAll('blockquote').forEach(b => {
      const t = b.textContent.trim();
      const k = kinds.find(([e]) => t.startsWith(e));
      if (k) b.classList.add(k[1]);
    });
    // tables
    art.querySelectorAll('table').forEach(t => {
      const w = document.createElement('div'); w.className = 'table-wrap';
      t.replaceWith(w); w.appendChild(t);
    });
    // toc
    const ol = app.querySelector('.toc ol');
    const hs = art.querySelectorAll('h2');
    hs.forEach((h, n) => {
      h.id = 'h-' + n;
      const li = document.createElement('li'), b = document.createElement('button');
      b.textContent = h.textContent;
      b.onclick = () => h.scrollIntoView({ behavior: 'smooth' });
      li.appendChild(b); ol.appendChild(li);
    });
    if (hs.length < 2) app.querySelector('.toc').remove();
    // external links
    art.querySelectorAll('a[href^="http"]').forEach(a => { a.target = '_blank'; a.rel = 'noopener'; });
    // code
    art.querySelectorAll('pre > code').forEach(code => {
      if (code.classList.contains('language-mermaid')) return;
      if (window.hljs && /language-/.test(code.className)) { try { window.hljs.highlightElement(code); } catch { /* ignore */ } }
      const btn = document.createElement('button');
      btn.className = 'copy'; btn.textContent = '複製';
      btn.onclick = async () => {
        try { await navigator.clipboard.writeText(code.textContent); btn.textContent = '已複製'; }
        catch { btn.textContent = '無法複製'; }
        setTimeout(() => { btn.textContent = '複製'; }, 1400);
      };
      code.parentElement.appendChild(btn);
    });
    // done button
    const btn = app.querySelector('.donebtn');
    const paint = () => { const on = read.has(id); btn.classList.toggle('is', on); btn.textContent = on ? '✓ 已複習（點擊取消）' : '標記為已複習'; };
    btn.onclick = () => { read.has(id) ? read.delete(id) : read.add(id); store.set('kb.read', [...read]); paint(); };
    paint();

    renderMermaid(art);
  }

  let mermaidLoading = null;
  function loadMermaid() {
    if (!mermaidLoading) {
      mermaidLoading = new Promise((res, rej) => {
        const s = document.createElement('script');
        s.src = MERMAID_SRC; s.onload = res; s.onerror = () => { mermaidLoading = null; rej(new Error('mermaid load failed')); };
        document.head.appendChild(s);
      }).then(() => {
        const dark = matchMedia('(prefers-color-scheme: dark)').matches;
        window.mermaid.initialize({
          startOnLoad: false, theme: dark ? 'dark' : 'default', securityLevel: 'strict',
          fontFamily: 'inherit', flowchart: { useMaxWidth: true, htmlLabels: true }, sequence: { useMaxWidth: true }
        });
      });
    }
    return mermaidLoading;
  }
  async function renderMermaid(root) {
    const codes = root.querySelectorAll('pre > code.language-mermaid');
    if (!codes.length) return;
    try { await loadMermaid(); } catch { return; } // offline: keep source text
    const nodes = [];
    codes.forEach(code => {
      const div = document.createElement('div');
      div.className = 'mermaid'; div.textContent = code.textContent;
      div.title = '點一下可放大／還原';
      div.onclick = () => div.classList.toggle('zoom');
      code.parentElement.replaceWith(div); nodes.push(div);
    });
    for (const n of nodes) {
      try { await window.mermaid.run({ nodes: [n] }); }
      catch (e) { console.error('mermaid', e); }
    }
  }

  function route() {
    if (!IDX) return;
    const [view, arg] = location.hash.replace(/^#\/?/, '').split('/');
    if (view === 'doc') return doc(arg);
    if (view === 'cat') return category(arg);
    if (view === 'path') return path();
    if (view === 'search') return search();
    home();
  }

  async function boot() {
    try {
      IDX = await (await fetch('content/index.json', { cache: 'no-cache' })).json();
    } catch (e) {
      app.innerHTML = '<p class="empty">無法載入目錄 content/index.json。<br>請透過網站網址或本機伺服器開啟（不能直接雙擊 index.html）。</p>';
      return;
    }
    route();
    // 讓 service worker 預先快取所有文章，之後離線也能閱讀
    if ('serviceWorker' in navigator && location.protocol.startsWith('http')) {
      navigator.serviceWorker.ready.then(reg => {
        if (reg.active) reg.active.postMessage({ precache: IDX.docs.map(d => d.file) });
      }).catch(() => {});
    }
  }
  window.addEventListener('hashchange', route);
  window.addEventListener('DOMContentLoaded', boot);
  if ('serviceWorker' in navigator && location.protocol.startsWith('http')) {
    window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
  }
})();
