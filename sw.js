const CACHE_NAME = 'iccmafia-v5';
const CORE_PAGES = [
  '/ICCMAFIA/',
  '/ICCMAFIA/index.html',
  '/ICCMAFIA/journal.html',
  '/ICCMAFIA/cheat-sheet.html',
  '/ICCMAFIA/psychology.html',
  '/ICCMAFIA/calendar.html',
  '/ICCMAFIA/comments.html',
  '/ICCMAFIA/podcast-assets.html',
  '/ICCMAFIA/disclosure.html'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(CORE_PAGES)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  const isCorePage = CORE_PAGES.some(p => url.pathname === p || url.pathname.endsWith(p));

  if (isCorePage) {
    // Network-first for HTML pages: always try to get fresh version,
    // fall back to cache only when offline
    event.respondWith(
      fetch(event.request).then(response => {
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      }).catch(() => caches.match(event.request))
    );
  } else {
    // Cache-first for assets (mp3, png, pdf, json, etc.)
    event.respondWith(
      caches.match(event.request).then(cached => {
        if (cached) return cached;
        return fetch(event.request).then(response => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          }
          return response;
        });
      })
    );
  }
});
