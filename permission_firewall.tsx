import React, { useState, useEffect } from 'react';
import { Shield, Mic, Camera, MapPin, FileText, Clock, AlertTriangle, CheckCircle, XCircle, Info, Ban, Check } from 'lucide-react';

const PermissionFirewall = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [showAlert, setShowAlert] = useState(false);
  const [alertData, setAlertData] = useState(null);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Simulate malicious behavior detection - every 2 minutes
  useEffect(() => {
    const anomalyDetections = [
      {
        appName: 'unknown-extension',
        permission: 'Camera, Microphone, Files',
        isAfterUpdate: false,
        updateType: 'New Extension Installed',
        anomalyScore: 92,
        details: 'Suspicious extension attempting unauthorized access to sensitive permissions'
      },
      {
        appName: 'Slack',
        permission: 'Location',
        isAfterUpdate: true,
        updateType: 'App Update v4.2.1',
        anomalyScore: 68,
        details: 'Unusual location permission access after recent update'
      },
      {
        appName: 'Chrome - ad-tracker.site',
        permission: 'Microphone, Camera, Clipboard',
        isAfterUpdate: false,
        updateType: 'New Website Opened',
        anomalyScore: 95,
        details: 'Malicious website attempting to access multiple sensitive permissions'
      },
      {
        appName: 'Discord',
        permission: 'Files, Location',
        isAfterUpdate: true,
        updateType: 'App Update v1.0.9',
        anomalyScore: 55,
        details: 'New file access pattern detected after update'
      },
      {
        appName: 'system32.exe',
        permission: 'Camera, Microphone, Files, Location',
        isAfterUpdate: false,
        updateType: 'New Process Started',
        anomalyScore: 98,
        details: 'Critical: Suspicious system process attempting broad permission access'
      }
    ];

    let currentIndex = 0;

    // Show first alert immediately
    const showAlert = () => {
      const detection = anomalyDetections[currentIndex];
      triggerAlert({
        ...detection,
        accessTime: new Date().toLocaleTimeString(),
        updateTime: new Date(Date.now() - 20000).toLocaleTimeString()
      });
      currentIndex = (currentIndex + 1) % anomalyDetections.length;
    };

    // First alert after 3 seconds
    const initialTimer = setTimeout(showAlert, 3000);

    // Then every 2 minutes (120000 ms)
    const intervalTimer = setInterval(showAlert, 120000);

    return () => {
      clearTimeout(initialTimer);
      clearInterval(intervalTimer);
    };
  }, []);

  const installedApps = [
    { name: 'Zoom', permissions: ['Microphone', 'Camera', 'Location'] },
    { name: 'Slack', permissions: ['Microphone', 'Files', 'Location'] },
    { name: 'Discord', permissions: ['Microphone', 'Camera'] },
    { name: 'Spotify', permissions: ['Files', 'Microphone'] },
    { name: 'Teams', permissions: ['Microphone', 'Camera', 'Files'] }
  ];

  const runningApps = [
    { name: 'Zoom', permission: 'Microphone', time: '10:23 AM', threat: 'Safe' },
    { name: 'Discord', permission: 'Camera', time: '10:24 AM', threat: 'Safe' },
    { name: 'Slack', permission: 'Location', time: '10:25 AM', threat: 'Medium' },
    { name: 'Spotify', permission: 'Files', time: '10:26 AM', threat: 'Safe' },
    { name: 'Chrome', permission: 'Microphone', time: '10:27 AM', threat: 'Threat' }
  ];

  const chromeTabs = [
    { name: 'YouTube', permissions: ['Microphone', 'Camera'] },
    { name: 'Google Meet', permissions: ['Microphone', 'Camera', 'Location'] },
    { name: 'Gmail', permissions: ['Files'] },
    { name: 'Facebook', permissions: ['Microphone', 'Location'] }
  ];

  const suspiciousTabs = [
    { name: 'ad-tracker.site', threat: 85, status: 'High Risk' },
    { name: 'unknown-extension', threat: 72, status: 'Medium Risk' },
    { name: 'YouTube', threat: 15, status: 'Low Risk' },
    { name: 'Gmail', threat: 5, status: 'Safe' }
  ];

  const triggerAlert = (data) => {
    setAlertData(data);
    setShowAlert(true);
  };

  const handleAllow = () => {
    console.log('Permission ALLOWED for:', alertData.appName);
    setShowAlert(false);
  };

  const handleDeny = () => {
    console.log('Permission DENIED for:', alertData.appName);
    setShowAlert(false);
  };

  const getPermissionIcon = (permission) => {
    switch(permission.toLowerCase()) {
      case 'microphone': return <Mic className="w-4 h-4" />;
      case 'camera': return <Camera className="w-4 h-4" />;
      case 'location': return <MapPin className="w-4 h-4" />;
      case 'files': return <FileText className="w-4 h-4" />;
      default: return <Shield className="w-4 h-4" />;
    }
  };

  const getThreatBadge = (threat) => {
    const configs = {
      'Safe': { bg: 'bg-green-100', text: 'text-green-800', icon: CheckCircle },
      'Medium': { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: AlertTriangle },
      'Threat': { bg: 'bg-red-100', text: 'text-red-800', icon: XCircle }
    };
    const config = configs[threat] || configs['Safe'];
    const Icon = config.icon;
    return (
      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${config.bg} ${config.text} flex items-center gap-1`}>
        <Icon className="w-3 h-3" />
        {threat}
      </span>
    );
  };

  const getThreatColor = (percentage) => {
    if (percentage >= 70) return 'bg-red-500';
    if (percentage >= 40) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      {/* Alert Box - Small centered popup */}
      {showAlert && alertData && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-gradient-to-b from-gray-900 to-black rounded-xl shadow-2xl max-w-md w-full border-2 border-red-500 animate-pulse-border">
            {/* Alert Header */}
            <div className="bg-red-600 p-4 rounded-t-xl">
              <div className="flex items-center justify-center gap-3">
                <AlertTriangle className="w-8 h-8 text-white animate-bounce" />
                <h2 className="text-2xl font-bold text-white">ALERT! SUSPICIOUS</h2>
              </div>
            </div>

            {/* Alert Content */}
            <div className="p-6 space-y-4">
              {/* App Name */}
              <div className="text-center">
                <h3 className="text-xl font-bold text-white mb-1">{alertData.appName}</h3>
                <p className="text-gray-400 text-sm">Detected malicious behavior</p>
              </div>

              {/* What was accessed */}
              <div className="bg-red-950/30 rounded-lg p-3 border border-red-500/30">
                <h4 className="text-red-400 font-semibold text-sm mb-2">🔓 What was accessed?</h4>
                <div className="flex flex-wrap gap-2">
                  {alertData.permission.split(',').map((perm, idx) => (
                    <span key={idx} className="flex items-center gap-1 px-2 py-1 bg-red-500/30 text-red-200 rounded text-xs">
                      {getPermissionIcon(perm.trim())}
                      {perm.trim()}
                    </span>
                  ))}
                </div>
              </div>

              {/* When */}
              <div className="bg-slate-800/50 rounded-lg p-3">
                <h4 className="text-yellow-400 font-semibold text-sm mb-1">⏰ When?</h4>
                <p className="text-white text-sm">{alertData.accessTime}</p>
              </div>

              {/* Update Info */}
              <div className="bg-slate-800/50 rounded-lg p-3">
                <h4 className="text-yellow-400 font-semibold text-sm mb-1">📦 After Update/Download?</h4>
                <p className="text-white text-sm">{alertData.isAfterUpdate ? 'Yes - ' : 'No - '}{alertData.updateType}</p>
                <p className="text-gray-400 text-xs mt-1">Event time: {alertData.updateTime}</p>
              </div>

              {/* Anomaly Score */}
              <div className="bg-slate-800/50 rounded-lg p-3">
                <h4 className="text-yellow-400 font-semibold text-sm mb-2">📊 ANOMALY SCORE</h4>
                <div className="flex items-center gap-3">
                  <div className="flex-1">
                    <div className="w-full bg-gray-700 rounded-full h-4">
                      <div 
                        className={`h-4 rounded-full ${getThreatColor(alertData.anomalyScore)} flex items-center justify-end pr-2`}
                        style={{ width: `${alertData.anomalyScore}%` }}
                      >
                        <span className="text-white text-xs font-bold">{alertData.anomalyScore}%</span>
                      </div>
                    </div>
                  </div>
                  <span className="text-2xl font-bold text-red-400">{alertData.anomalyScore}</span>
                </div>
              </div>

              {/* Details */}
              <div className="bg-red-950/20 rounded-lg p-3 border border-red-500/20">
                <p className="text-gray-300 text-xs">{alertData.details}</p>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-2">
                <button 
                  onClick={handleDeny}
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-all"
                >
                  <Ban className="w-4 h-4" />
                  DENY
                </button>
                <button 
                  onClick={handleAllow}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-all"
                >
                  <Check className="w-4 h-4" />
                  ALLOW
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="mb-8 flex items-center justify-center gap-4">
        <Shield className="w-12 h-12 text-purple-400" />
        <h1 className="text-5xl font-bold text-white tracking-tight">
          Permission <span className="text-purple-400">~</span> Firewall
        </h1>
      </div>

      <div className="grid grid-cols-2 gap-6 max-w-7xl mx-auto">
        {/* LEFT SIDE */}
        <div className="space-y-6">
          {/* Top Left - Installed Apps */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-2xl">
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
              <Shield className="w-6 h-6 text-purple-400" />
              Installed Applications
            </h2>
            <div className="space-y-3">
              {installedApps.map((app, idx) => (
                <div key={idx} className="bg-white/5 rounded-xl p-4 hover:bg-white/10 transition-all">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="font-semibold text-white text-lg">{app.name}</div>
                    <div className="flex flex-wrap gap-2">
                      {app.permissions.map((perm, pidx) => (
                        <span key={pidx} className="flex items-center gap-1 px-3 py-1 bg-purple-500/30 text-purple-200 rounded-lg text-sm">
                          {getPermissionIcon(perm)}
                          {perm}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Bottom Left - Running Apps */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-2xl">
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
              <Clock className="w-6 h-6 text-green-400" />
              Live Activity Monitor
            </h2>
            <div className="space-y-3">
              {runningApps.map((app, idx) => (
                <div key={idx} className="bg-white/5 rounded-xl p-4 hover:bg-white/10 transition-all">
                  <div className="grid grid-cols-4 gap-3 items-center">
                    <div className="font-semibold text-white">{app.name}</div>
                    <div className="flex items-center gap-2 text-purple-300">
                      {getPermissionIcon(app.permission)}
                      <span className="text-sm">{app.permission}</span>
                    </div>
                    <div className="text-gray-300 text-sm">{app.time}</div>
                    <div className="flex justify-end">
                      {getThreatBadge(app.threat)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* RIGHT SIDE */}
        <div className="space-y-6">
          {/* Chrome Header */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-yellow-500 rounded-full flex items-center justify-center">
                  <span className="text-white font-bold">C</span>
                </div>
                Chrome Browser
              </h2>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-blue-500/30 text-blue-200 rounded-lg text-sm flex items-center gap-1">
                  <Mic className="w-3 h-3" />
                  Microphone
                </span>
                <span className="px-3 py-1 bg-blue-500/30 text-blue-200 rounded-lg text-sm flex items-center gap-1">
                  <Camera className="w-3 h-3" />
                  Camera
                </span>
                <span className="px-3 py-1 bg-blue-500/30 text-blue-200 rounded-lg text-sm flex items-center gap-1">
                  <MapPin className="w-3 h-3" />
                  Location
                </span>
              </div>
            </div>
          </div>

          {/* Top Right - Active Tabs */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-2xl">
            <h3 className="text-xl font-bold text-white mb-4">Active Tabs</h3>
            <div className="space-y-3">
              {chromeTabs.map((tab, idx) => (
                <div key={idx} className="bg-white/5 rounded-xl p-4 hover:bg-white/10 transition-all">
                  <div className="flex justify-between items-center">
                    <div className="font-medium text-white">{tab.name}</div>
                    <div className="flex gap-2">
                      {tab.permissions.map((perm, pidx) => (
                        <span key={pidx} className="flex items-center gap-1 px-2 py-1 bg-blue-500/30 text-blue-200 rounded-lg text-xs">
                          {getPermissionIcon(perm)}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Bottom Right - Suspicious Activity */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 shadow-2xl">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <AlertTriangle className="w-6 h-6 text-red-400" />
              Threat Analysis
            </h3>
            <div className="space-y-3">
              {suspiciousTabs.map((tab, idx) => (
                <div key={idx} className="bg-white/5 rounded-xl p-4 hover:bg-white/10 transition-all">
                  <div className="flex justify-between items-center mb-2">
                    <div className="font-medium text-white">{tab.name}</div>
                    <span className="text-sm font-semibold text-white">{tab.threat}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2 mb-2">
                    <div 
                      className={`h-2 rounded-full ${getThreatColor(tab.threat)} transition-all`}
                      style={{ width: `${tab.threat}%` }}
                    />
                  </div>
                  <div className="text-xs text-gray-300">{tab.status}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-6 text-center text-white/60 text-sm">
        Real-time monitoring active • Last updated: {currentTime.toLocaleTimeString()}
      </div>
    </div>
  );
};

export default PermissionFirewall;