def rule_based_check(app_name, permission, hour):
    """
    Returns: (is_threat, threat_level, reason)
    """
    app = app_name.lower().replace('.exe', '').strip()
    perm = permission.lower().strip()
    
    # CRITICAL rules (instant block recommendations)
    if app in ['calculator', 'notepad', 'wordpad'] and perm in ['camera', 'microphone']:
        return True, "CRITICAL", f"Utility app {app} should never access {perm}"
    
    if app in ['cmd', 'powershell'] and perm in ['camera', 'microphone', 'location']:
        return True, "CRITICAL", f"System tool {app} requesting {perm} is highly suspicious"
    
    # HIGH rules (suspicious timing/context)
    if perm in ['camera', 'microphone'] and (hour >= 0 and hour <= 5):
        return True, "HIGH", f"{perm.capitalize()} access at {hour}:00 (late night) is unusual"
    
    # No rule triggered
    return False, "LOW", "No rule violations"
