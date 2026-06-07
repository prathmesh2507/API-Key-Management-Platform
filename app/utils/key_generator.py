import secrets


def generate_api_key():
    prefix = "dg_live_"
    random_part = secrets.token_urlsafe(32)
    return prefix + random_part
