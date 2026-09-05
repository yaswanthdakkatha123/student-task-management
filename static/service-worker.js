self.addEventListener("install", event => {
    console.log("Service Worker installed");
    self.skipWaiting();
});

self.addEventListener("activate", event => {
    console.log("Service Worker activated");
});

self.addEventListener("fetch", event => {
    event.respondWith(fetch(event.request));
});
self.addEventListener("install", event => {
    console.log("Service Worker installed");
    self.skipWaiting();
});

self.addEventListener("activate", event => {
    console.log("Service Worker activated");
});

self.addEventListener("fetch", event => {
    event.respondWith(fetch(event.request));
});

// Notification click
self.addEventListener("notificationclick", event => {
    event.notification.close();

    event.waitUntil(
        clients.matchAll({
            type: "window",
            includeUncontrolled: true
        }).then(clientList => {
            for (const client of clientList) {
                if ("focus" in client) {
                    return client.focus();
                }
            }

            if (clients.openWindow) {
                return clients.openWindow("/");
            }
        })
    );
});
