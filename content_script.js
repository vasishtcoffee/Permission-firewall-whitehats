// content_script.js - Relay messages between page and extension

console.log('🔒 Permission Watcher: Content Script Active');
console.log('📍 Loaded on:', window.location.href);

// Listen for permission events from injected script (content_injector.js)
window.addEventListener('message', function(event) {
    // Security: only accept messages from same window
    if (event.source !== window) return;
    
    // Check if it's our permission detection event
    if (event.data && event.data.type === 'PERMISSION_DETECTED') {
        console.log('📨 Content Script: Permission event received!');
        console.log('   Permission:', event.data.permission);
        console.log('   Granted:', event.data.granted);
        console.log('   URL:', event.data.url);
        
        // Forward to background script with proper message type
        chrome.runtime.sendMessage({
            type: 'PERMISSION_EVENT',
            data: event.data
        }).then(response => {
            console.log('✅ Message sent to background:', response);
        }).catch(err => {
            console.error('❌ Error sending to background:', err);
        });
    }
});

// Inject the permission detector into page context
function injectPermissionDetector() {
    const script = document.createElement('script');
    script.src = chrome.runtime.getURL('content_injector.js');
    
    script.onload = function() {
        console.log('✅ Permission detector injected successfully');
        this.remove();
    };
    
    script.onerror = function() {
        console.error('❌ Failed to inject permission detector');
    };
    
    // Append to document
    (document.head || document.documentElement).appendChild(script);
}

// Inject on load
injectPermissionDetector();

console.log('✅ Content script initialization complete');
