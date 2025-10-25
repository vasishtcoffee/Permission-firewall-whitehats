// content_injector.js - Permission Detection & Interception

(function() {
    'use strict';
    
    console.log('🔒 Permission Firewall: Injected into page');
    
    // Store original API methods
    const originalGetUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
    const originalGeolocation = navigator.geolocation.getCurrentPosition.bind(navigator.geolocation);
    const originalNotification = window.Notification ? window.Notification.requestPermission.bind(window.Notification) : null;
    
    // Helper function to send permission event
    function sendPermissionEvent(permissionType, origin, granted) {
        const event = {
            type: 'PERMISSION_DETECTED',
            permission: permissionType,
            origin: window.location.origin,
            url: window.location.href,
            timestamp: new Date().toISOString(),
            granted: granted
        };
        
        console.log('🔔 Permission Event:', event);
        
        // Send to content script
        window.postMessage(event, '*');
        
        // Also send directly to extension
        if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.sendMessage) {
            chrome.runtime.sendMessage(event).catch(err => {
                console.log('Extension context unavailable:', err);
            });
        }
    }
    
    // Override getUserMedia (Camera/Microphone)
    navigator.mediaDevices.getUserMedia = function(constraints) {
        console.log('📹 Camera/Mic request detected:', constraints);
        
        const permissionType = constraints.video ? 
            (constraints.audio ? 'camera_microphone' : 'camera') : 
            'microphone';
        
        // Send detection event immediately
        sendPermissionEvent(permissionType, window.location.origin, 'pending');
        
        return originalGetUserMedia(constraints)
            .then(stream => {
                console.log('✅ Permission GRANTED:', permissionType);
                sendPermissionEvent(permissionType, window.location.origin, true);
                return stream;
            })
            .catch(error => {
                console.log('❌ Permission DENIED:', permissionType);
                sendPermissionEvent(permissionType, window.location.origin, false);
                throw error;
            });
    };
    
    // Override Geolocation
    navigator.geolocation.getCurrentPosition = function(success, error, options) {
        console.log('📍 Location request detected');
        sendPermissionEvent('location', window.location.origin, 'pending');
        
        const wrappedSuccess = function(position) {
            console.log('✅ Location permission GRANTED');
            sendPermissionEvent('location', window.location.origin, true);
            if (success) success(position);
        };
        
        const wrappedError = function(err) {
            console.log('❌ Location permission DENIED');
            sendPermissionEvent('location', window.location.origin, false);
            if (error) error(err);
        };
        
        return originalGeolocation(wrappedSuccess, wrappedError, options);
    };
    
    // Override Notification
    if (originalNotification) {
        window.Notification.requestPermission = function() {
            console.log('🔔 Notification request detected');
            sendPermissionEvent('notification', window.location.origin, 'pending');
            
            return originalNotification().then(result => {
                console.log('✅ Notification permission:', result);
                sendPermissionEvent('notification', window.location.origin, result === 'granted');
                return result;
            });
        };
    }
    
    // Monitor permission changes via Permissions API
    if (navigator.permissions && navigator.permissions.query) {
        ['camera', 'microphone', 'geolocation', 'notifications'].forEach(permName => {
            navigator.permissions.query({ name: permName }).then(permissionStatus => {
                console.log(`📊 Initial ${permName} status:`, permissionStatus.state);
                
                permissionStatus.onchange = function() {
                    console.log(`🔄 ${permName} permission changed to:`, this.state);
                    sendPermissionEvent(permName, window.location.origin, this.state === 'granted');
                };
            }).catch(err => {
                console.log(`Cannot query ${permName}:`, err.message);
            });
        });
    }
    
    console.log('✅ Permission Firewall: All hooks installed');
})();
