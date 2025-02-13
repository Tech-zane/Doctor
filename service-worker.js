const CACHE_NAME = "digidoc-cache-v1";
const urlsToCache = [
  "/", 
  "/manifest.json",
  // Add any other files or paths you want cached
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("Opened cache");
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      // Return cached response if available; otherwise fetch from network.
      return response || fetch(event.request);
    })
  );
});
