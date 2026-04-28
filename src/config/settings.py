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


def load_settings() -> Settings:
    username = os.getenv("X_USERNAME", "")
    password = os.getenv("X_PASSWORD", "")

    if not username or not password:
        raise ValueError(
            "X_USERNAME and X_PASSWORD must be set in .env file. "
            "See .env.example for reference."
        )

    return Settings(
        x_username=username,
        x_password=password,
    )
