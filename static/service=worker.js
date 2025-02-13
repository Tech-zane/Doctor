const CACHE_NAME = "digidoc-cache-v2";  // Changed version for future updates
const OFFLINE_URL = '/static/offline.html';  // Add an offline fallback page
const STATIC_ASSETS = [
  '/',
  '/static/manifest.json',  // Correct path for Streamlit
  '/static/service-worker.js',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  // Add other core assets like CSS/JS if you have them
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Caching core assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('[Service Worker] Removing old cache:', cache);
            return caches.delete(cache);
          }
        })
      );
    })
  );
});

self.addEventListener('fetch', (event) => {
  // Network-first strategy for navigation requests
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .catch(() => caches.match(OFFLINE_URL))
    );
  } else {
    // Cache-first strategy for static assets
    event.respondWith(
      caches.match(event.request)
        .then((response) => {
          return response || fetch(event.request)
            .then((fetchResponse) => {
              // Cache new resources as they are fetched
              return caches.open(CACHE_NAME)
                .then((cache) => {
                  cache.put(event.request.url, fetchResponse.clone());
                  return fetchResponse;
                });
            })
            .catch(() => {
              // Return offline page for failed requests
              if (event.request.headers.get('accept').includes('text/html')) {
                return caches.match(OFFLINE_URL);
              }
            });
        })
    );
  }
});
