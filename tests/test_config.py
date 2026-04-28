"""Test suite for config/settings.py"""
import pytest
import os
from unittest.mock import patch


def test_load_settings_returns_username():
    with patch.dict(os.environ, {
        "X_USERNAME": "testuser",
        "X_PASSWORD": "testpass",
    }):
        from src.config.settings import load_settings
        settings = load_settings()
        assert settings.x_username == "testuser"


def test_load_settings_returns_password():
    with patch.dict(os.environ, {
        "X_USERNAME": "testuser",
        "X_PASSWORD": "testpass",
    }):
        from src.config.settings import load_settings
        settings = load_settings()
        assert settings.x_password == "testpass"


def test_load_settings_raises_when_missing_username():
    with patch.dict(os.environ, {"X_PASSWORD": "pass"}, clear=False):
        with pytest.raises(ValueError, match="X_USERNAME"):
            from src.config.settings import load_settings
            load_settings()


def test_settings_defaults():
    with patch.dict(os.environ, {
        "X_USERNAME": "user",
        "X_PASSWORD": "pass",
    }):
        from src.config.settings import load_settings
        settings = load_settings()
        assert settings.default_tweet_count == 200
        assert settings.max_retries == 3
        assert settings.retry_delay == 5.0
