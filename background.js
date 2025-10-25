// background.js - Permission Watcher Extension with ML Backend Integration

console.log("🔒 Permission Watcher extension loaded successfully!");

// Backend API URL
const API_URL = 'http://localhost:8000';

// Storage for tracking permission usage
let permissionLog = [];
let suspiciousActivity = [];

// ============================================
// INITIALIZATION
// ============================================
chrome.runtime.onInstalled.addListener(() => {
  console.log("✅ Extension installed/updated at:", new Date().toLocaleString());
  
  // Show welcome notification
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icon48.png',
    title: '🔒 Permission Watcher Active',
    message: 'Now monitoring permission usage with ML-powered threat detection'
  });
  
  // Initialize storage
  chrome.storage.local.set({
    permissionLog: [],
    suspiciousActivity: [],
    isMonitoring: true
  });
  
  // Test backend connection
  testBackendConnection();
});

// ============================================
// TEST BACKEND CONNECTION
// ============================================
async function testBackendConnection() {
  try {
    console.log('🔌 Testing ML backend connection...');
    const response = await fetch(API_URL);
    const data = await response.json();
    
    console.log('✅ Backend connected:', data);
    
    if (data.model_loaded) {
      console.log('🤖 Isolation Forest model loaded and ready!');
    } else {
      console.warn('⚠️ ML model not loaded in backend');
    }
  } catch (error) {
    console.error('❌ Cannot connect to backend:', error.message);
    console.warn('⚠️ Make sure FastAPI is running: python -m uvicorn main:app --reload --port 8000');
  }
}

// ============================================
// MAIN MESSAGE HANDLER (Content Script Communication)
// ============================================
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log("📨 Message received:", message.type);
  
  // THIS is the critical handler for permission events
  if (message.type === 'PERMISSION_EVENT') {
    console.log("🚨 PERMISSION EVENT DETECTED!");
    console.log("   Permission:", message.data.permission);
    console.log("   URL:", message.data.url);
    console.log("   Granted:", message.data.granted);
    
    handlePermissionEvent(message.data, sender.tab)
      .then(response => {
        console.log("✅ Analysis complete:", response);
        sendResponse(response);
      })
      .catch(error => {
        console.error("❌ Error:", error);
        sendResponse({ success: false, error: error.message });
      });
    
    return true; // Keep channel open for async response
  }
  
  // Legacy handlers (keep for compatibility)
  if (message.type === 'PERMISSION_REQUEST') {
    handleLegacyPermissionRequest(message, sender.tab);
  }
  
  if (message.type === 'PERMISSION_GRANTED') {
    handleLegacyPermissionGranted(message, sender.tab);
  }
  
  if (message.type === 'CONTENT_SCRIPT_LOADED') {
    console.log("✅ Content script loaded on:", message.url);
  }
  
  sendResponse({ received: true });
  return true;
});

// ============================================
// HANDLE PERMISSION EVENT (Main ML Analysis)
// ============================================
async function handlePermissionEvent(eventData, tab) {
  try {
    const hostname = new URL(tab.url).hostname;
    
    console.log('🔍 Analyzing permission request from:', hostname);
    
    // Prepare data for ML backend
    const requestData = {
      app_name: hostname,
      permission_type: eventData.permission,
      timestamp: eventData.timestamp,
      url: tab.url
    };
    
    console.log('📤 Sending to Isolation Forest backend:', requestData);
    
    // Send to FastAPI backend with ML model
    const response = await fetch(`${API_URL}/check-permission`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData)
    });
    
    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }
    
    const result = await response.json();
    
    console.log('📥 ML ANALYSIS RESULT:');
    console.log('   Threat Level:', result.threat_level);
    console.log('   Anomaly Score:', result.anomaly_score);
    console.log('   Reason:', result.reason);
    console.log('   Layers:', result.layers_triggered);
    
    // Log the activity
    const activity = {
      type: 'PERMISSION_DETECTED',
      permission: eventData.permission,
      url: tab.url,
      tabId: tab.id,
      timestamp: eventData.timestamp,
      granted: eventData.granted,
      mlAnalysis: result
    };
    
    logPermissionActivity(activity);
    
    // Show notification based on ML threat assessment
    showMLNotification(result, hostname, eventData.permission);
    
    // Flag if suspicious
    if (result.threat_level === 'high' || result.threat_level === 'critical') {
      suspiciousActivity.push(activity);
      chrome.storage.local.set({ suspiciousActivity: suspiciousActivity });
    }
    
    return {
      success: true,
      analysis: result
    };
    
  } catch (error) {
    console.error('❌ Backend communication error:', error);
    
    // Show fallback notification
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icon48.png',
      title: '⚠️ Permission Detected',
      message: `${eventData.permission} requested (Backend unavailable)`,
      priority: 1
    });
    
    // Still log the activity even if backend fails
    logPermissionActivity({
      type: 'PERMISSION_DETECTED',
      permission: eventData.permission,
      url: tab.url,
      tabId: tab.id,
      timestamp: eventData.timestamp,
      error: error.message
    });
    
    return {
      success: false,
      error: error.message
    };
  }
}

// ============================================
// SHOW ML-POWERED NOTIFICATION
// ============================================
function showMLNotification(analysis, hostname, permission) {
  const threatEmojis = {
    'low': '✅',
    'medium': '⚠️',
    'high': '🚨',
    'critical': '🔴'
  };
  
  const emoji = threatEmojis[analysis.threat_level] || '🔔';
  const priority = (analysis.threat_level === 'high' || analysis.threat_level === 'critical') ? 2 : 1;
  
  // Only show notification for medium and above
  if (analysis.threat_level !== 'low') {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icon48.png',
      title: `${emoji} ${analysis.threat_level.toUpperCase()} Threat Detected`,
      message: `Site: ${hostname}\nPermission: ${permission}\n\n${analysis.reason}\n\nML Anomaly Score: ${(analysis.anomaly_score * 100).toFixed(1)}%\nDetection Layers: ${analysis.layers_triggered.join(', ')}`,
      priority: priority,
      requireInteraction: analysis.threat_level === 'critical'
    });
    
    console.log(`🔔 ${analysis.threat_level} threat notification shown`);
  } else {
    console.log('✅ Low threat - no notification needed');
  }
}

// ============================================
// LEGACY HANDLERS (For Compatibility)
// ============================================
function handleLegacyPermissionRequest(data, tab) {
  console.log("⚠️ Legacy permission request:", data.permission, "on", tab.url);
  
  const activity = {
    type: 'PERMISSION_REQUEST',
    permission: data.permission,
    url: tab.url,
    tabId: tab.id,
    timestamp: Date.now()
  };
  
  logPermissionActivity(activity);
  checkSuspiciousActivity(activity);
}

function handleLegacyPermissionGranted(data, tab) {
  console.log("✅ Legacy permission granted:", data.permission, "on", tab.url);
  
  const activity = {
    type: 'PERMISSION_GRANTED',
    permission: data.permission,
    url: tab.url,
    tabId: tab.id,
    timestamp: Date.now()
  };
  
  logPermissionActivity(activity);
}

// ============================================
// ACTIVITY LOGGING
// ============================================
function logPermissionActivity(activity) {
  permissionLog.push(activity);
  
  // Keep only last 500 entries
  if (permissionLog.length > 500) {
    permissionLog = permissionLog.slice(-500);
  }
  
  // Save to storage
  chrome.storage.local.set({ permissionLog: permissionLog });
  
  console.log(`💾 Activity logged (Total: ${permissionLog.length})`);
}

// ============================================
// SIMPLE RULE-BASED CHECK (Fallback)
// ============================================
function checkSuspiciousActivity(activity) {
  const sensitivePermissions = [
    'camera', 
    'microphone', 
    'camera_microphone',
    'camera_and_microphone', 
    'geolocation', 
    'notifications', 
    'screen_capture', 
    'bluetooth', 
    'usb', 
    'clipboard_read'
  ];
  
  if (sensitivePermissions.includes(activity.permission)) {
    console.warn("🚨 Sensitive permission detected:", activity);
    
    suspiciousActivity.push(activity);
    chrome.storage.local.set({ suspiciousActivity: suspiciousActivity });
  }
}

// ============================================
// TAB MONITORING (Optional - for debugging)
// ============================================
chrome.tabs.onCreated.addListener((tab) => {
  console.log("📂 New tab created:", tab.id);
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    console.log("🌐 Page loaded:", tab.url);
  }
});

// ============================================
// NOTIFICATION CLICK HANDLER
// ============================================
chrome.notifications.onClicked.addListener((notificationId) => {
  console.log("🔔 Notification clicked:", notificationId);
  // You could open a dashboard or show details here
});

// ============================================
// STARTUP
// ============================================
console.log("🔒 Permission Watcher is now monitoring all tabs");
console.log("🤖 ML-powered threat detection enabled");
console.log("⏳ Waiting for permission events...");

// Test backend on startup
testBackendConnection();
