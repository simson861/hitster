// Offline support: app files cache-first, Google Fonts cached as they are fetched.
const CACHE = 'hitlinie-__BUILD__';
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
  e.respondWith(caches.match(e.request, { ignoreSearch: same }).then(hit => {
    const net = fetch(e.request).then(res => {
      if (res.ok || res.type === 'opaque') caches.open(CACHE).then(c => c.put(e.request, res.clone()));
      return res;
    });
    return hit || net;
  }));
});
