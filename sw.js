const CACHE_NAME = 'iccmafia-v1';
const CORE_PAGES = [
  '/ICCMAFIA/',
  '/ICCMAFIA/index.html',
  '/ICCMAFIA/journal.html',
  '/ICCMAFIA/cheat-sheet.html',
  '/ICCMAFIA/psychology.html',
  '/ICCMAFIA/calendar.html'
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
  // Only handle GET requests
  if (event.request.method !== 'GET') return;
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request).then(response => {
        // Cache successful responses for core pages
        if (response && response.status === 200) {
          const url = new URL(event.request.url);
          if (CORE_PAGES.some(p => url.pathname === p || url.pathname.endsWith(p))) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          }
        }
        return response;
      }).catch(() => cached); // fallback to cache on network failure
    })
  );
});
