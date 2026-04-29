from pathlib import Path
from dataclasses import dataclass
import os

from dotenv import load_dotenv

# Resolve .env from project root (parent of src/)
ENV_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(ENV_PATH)


@dataclass
class Settings:
    x_username: str
    x_password: str
    default_tweet_count: int = 200
    max_retries: int = 3
    retry_delay: float = 5.0
    cookies: dict = None

    def __post_init__(self):
        if self.cookies is None:
            self.cookies = {}


def _load_cookies() -> dict:
    """Load X.com cookies from environment variables."""
    cookie_prefix = "X_COOKIE_"
    cookies = {}

    for key, value in os.environ.items():
        if key.startswith(cookie_prefix):
            cookie_name = key[len(cookie_prefix):].lower()
            cookies[cookie_name] = value

    return cookies


def load_settings() -> Settings:
    username = os.getenv("X_USERNAME", "")
    password = os.getenv("X_PASSWORD", "")
    cookies = _load_cookies()

    # Check if we have cookies or credentials
    if not cookies and (not username or not password):
        raise ValueError(
            "Missing authentication. Please set either:\n"
            "  - X_COOKIE_AUTH_TOKEN and X_COOKIE_CT0 (recommended), OR\n"
            "  - X_USERNAME and X_PASSWORD\n"
            "See .env.example for reference."
        )

    return Settings(
        x_username=username,
        x_password=password,
        cookies=cookies,
    )
