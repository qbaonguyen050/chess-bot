const CACHE_NAME = 'offline-chess-v1';
// List of files to cache. The chess.min.js is crucial.
const urlsToCache = [
    './offline_chess.html',
    'https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.10.3/chess.min.js'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Cache hit - return response
                if (response) {
                    return response;
                }
                return fetch(event.request);
            })
    );
});