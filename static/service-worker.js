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

<script>
if ("Notification" in window) {
    Notification.requestPermission().then(function(permission) {
        console.log("Notification permission:", permission);
    });
}
</script>
