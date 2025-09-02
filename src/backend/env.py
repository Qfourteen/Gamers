import os
from pathlib import Path


def _read_file(path: str) -> str | None:
    try:
        p = Path(path)
        if p.is_file():
            return p.read_text(encoding="utf-8").strip()
    except Exception:
        pass
    return None


def _get_secret(name: str, default: str | None = None) -> str | None:
    """Return secret from NAME_FILE or NAME env var, else default.

    Supports Docker/Podman-style *_FILE pattern. If both are set, *_FILE wins.
    """
    file_var = os.getenv(f"{name}_FILE")
    if file_var:
        content = _read_file(file_var)
        if content is not None:
            return content
    return os.getenv(name, default)


def _get_bool(name: str, default: bool = False) -> bool:
    raw = _get_secret(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


# Database URL. Override via MONGODB_URL or MONGODB_URL_FILE.
MONGODB_URL = _get_secret("MONGODB_URL", "mongodb://localhost:27017")

# Cookie security flag. Override via SECURE_COOKIE or SECURE_COOKIE_FILE.
SECURE_COOKIE = _get_bool("SECURE_COOKIE", True)

# App secret key. Provide securely via SECRET_KEY or SECRET_KEY_FILE.
# NOTE: Do NOT use the default in production; inject via secrets.
SECRET_KEY = _get_secret("SECRET_KEY", "change-me")
