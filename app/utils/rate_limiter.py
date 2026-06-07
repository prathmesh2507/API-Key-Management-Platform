from datetime import datetime, timedelta


def check_rate_limit(api_key_doc):
    now = datetime.utcnow()

    window_start = api_key_doc.get("window_start")
    rate_limit = api_key_doc.get("rate_limit_per_minute")
    request_count = api_key_doc.get("request_count", 0)

    # If window expired (older than 60 seconds)
    if now - window_start > timedelta(seconds=60):
        return {
            "allowed": True,
            "reset": True,
            "new_window_start": now
        }

    # If limit exceeded
    if request_count >= rate_limit:
        return {
            "allowed": False
        }

    return {
        "allowed": True,
        "reset": False
    }
