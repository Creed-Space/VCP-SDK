/**
 * VCP Demo Service Worker
 * Provides offline support and caching for the demo site
 */

const CACHE_NAME = 'vcp-demo-v1';

// Resources to cache on install
const PRECACHE_RESOURCES = [
	'/',
	'/about',
	'/demos',
	'/playground',
	'/docs',
	'/docs/getting-started',
	'/docs/concepts',
	'/docs/csm1-specification',
	'/manifest.json',
	'/vcp-logo.png',
	'/favicon.png'
];

// Install event - precache core resources
self.addEventListener('install', (event) => {
	event.waitUntil(
		caches.open(CACHE_NAME).then((cache) => {
			console.log('[SW] Precaching core resources');
			return cache.addAll(PRECACHE_RESOURCES);
		})
	);
	// Activate immediately
	self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
	event.waitUntil(
		caches.keys().then((cacheNames) => {
			return Promise.all(
				cacheNames
					.filter((name) => name !== CACHE_NAME)
					.map((name) => {
						console.log('[SW] Deleting old cache:', name);
						return caches.delete(name);
					})
			);
		})
	);
	// Take control of all pages immediately
	self.clients.claim();
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
	const { request } = event;

	// Skip non-GET requests
	if (request.method !== 'GET') return;

	// Skip external requests
	if (!request.url.startsWith(self.location.origin)) return;

	// Skip API requests (if any)
	if (request.url.includes('/api/')) return;

	event.respondWith(
		caches.match(request).then((cachedResponse) => {
			// Return cached response if available
			if (cachedResponse) {
				// Fetch and update cache in background (stale-while-revalidate)
				event.waitUntil(
					fetch(request)
						.then((response) => {
							if (response.ok) {
								caches.open(CACHE_NAME).then((cache) => {
									cache.put(request, response);
								});
							}
						})
						.catch(() => {
							// Network error, ignore
						})
				);
				return cachedResponse;
			}

			// Not in cache, fetch from network
			return fetch(request)
				.then((response) => {
					// Cache successful responses
					if (response.ok) {
						const responseClone = response.clone();
						caches.open(CACHE_NAME).then((cache) => {
							cache.put(request, responseClone);
						});
					}
					return response;
				})
				.catch(() => {
					// Network error and not in cache
					// Return offline page for navigation requests
					if (request.mode === 'navigate') {
						return caches.match('/');
					}
					// Return empty response for other resources
					return new Response('', { status: 503, statusText: 'Service Unavailable' });
				});
		})
	);
});

// Handle messages from the page
self.addEventListener('message', (event) => {
	if (event.data === 'skipWaiting') {
		self.skipWaiting();
	}
});
