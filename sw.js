// Offline support: the app's own files come from the network first so updates show up at once,
// the cached copy is only used offline; Google Fonts are cache-first since they never change.
const CACHE = 'hitlinie-73b169fa00';
const APP = ['./', './index.html', './manifest.webmanifest', './icons/icon-192.png', './icons/icon-512.png', './icons/apple-touch-icon.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(APP)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  const same = url.origin === location.origin;
  const font = url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com';
  if (!same && !font) return;
  if (same && url.pathname.endsWith('/version.json')) return; // always asked from the network by the update check
  const store = res => {
    if (res.ok || res.type === 'opaque') { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
    return res;
  };
  if (font) {
    e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(store)));
    return;
  }
  e.respondWith(fetch(e.request, { cache: 'no-cache' }).then(store)
    .catch(() => caches.match(e.request, { ignoreSearch: true }).then(hit => hit || caches.match('./index.html'))));
});
