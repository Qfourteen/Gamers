from datetime import datetime, timezone

def utc_now_factory(tz=timezone.utc):
    return datetime.now(tz)