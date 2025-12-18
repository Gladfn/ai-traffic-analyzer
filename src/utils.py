def ip_to_int(ip):
    if not ip or not isinstance(ip, str):
        return 0
    try:
        return int(''.join([f"{int(octet):03d}" for octet in ip.split('.')]))
    except Exception:
        return 0
