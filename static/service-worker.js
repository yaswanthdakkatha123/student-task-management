self.addEventListener("install", event => {
    console.log("Service Worker installed");
    self.skipWaiting();
});

self.addEventListener("activate", event => {
    console.log("Service Worker activated");
    event.waitUntil(self.clients.claim());
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

// Show notification when requested by webpage
self.addEventListener("message", event => {

    if (event.data && event.data.type === "SHOW_NOTIFICATION") {

        self.registration.showNotification(
            event.data.title,
            {
                body: event.data.body,
                icon: "/static/icon.png",
                badge: "/static/icon.png"
            }
        );

    }
});
