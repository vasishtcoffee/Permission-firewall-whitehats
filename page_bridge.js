// page_bridge.js - runs in extension context and bridges messages between page and background

console.log('[Permission Watcher] Page bridge initialized');

window.addEventListener('message', (event) => {
  // Only accept messages from the same window
  if (event.source !== window || !event.data || event.data.direction !== 'to_extension') return;
  
  const payload = event.data.payload;
  const messageId = event.data.id;
  
  // Forward to background
  chrome.runtime.sendMessage(payload, (reply) => {
    if (chrome.runtime.lastError) {
      console.error('[Permission Watcher] Background error:', chrome.runtime.lastError);
      // Send error response back to page
      window.postMessage({ 
        direction: 'from_extension_reply', 
        payload: { action: 'allow' }, // Default to allow on error
        id: messageId 
      }, '*');
      return;
    }
    
    // Send response back to page
    window.postMessage({ 
      direction: 'from_extension_reply', 
      payload: reply,
      id: messageId 
    }, '*');
  });
});

// Also listen for background push messages to forward to page if needed
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  // Forward to page if needed
  window.postMessage({ direction: 'from_extension_background', payload: msg }, '*');
  sendResponse({ ok: true });
});
