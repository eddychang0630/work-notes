// Service worker：同站資源「網路優先、離線退回快取」，CDN 函式庫「快取優先」。
const CACHE = 'kb-v1';
const SHELL = ['./', 'index.html', 'assets/app.css', 'assets/app.js', 'assets/icon.svg', 'content/index.json'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('message', async e => {
  // 首次開啟後由頁面要求預先快取所有文章，之後可完全離線閱讀
  if (e.data && e.data.precache) {
    const c = await caches.open(CACHE);
    await Promise.all(e.data.precache.map(u => c.add(u).catch(() => {})));
  }
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const same = new URL(req.url).origin === location.origin;
  if (same) {
    e.respondWith(
      fetch(req).then(res => {
        if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
        return res;
      }).catch(() => caches.match(req, { ignoreSearch: true }).then(r => r || caches.match('index.html')))
    );
  } else {
    e.respondWith(
      caches.match(req).then(hit => hit || fetch(req).then(res => {
        if (res.ok || res.type === 'opaque') { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
        return res;
      }))
    );
  }
});
