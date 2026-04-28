"""Test suite for src/engine/preprocessor.py"""
import pytest
from src.engine.preprocessor import clean_tweet


def test_remove_mentions():
    assert clean_tweet("@john hello world") == "hello world"


def test_remove_urls():
    assert clean_tweet("Check this https://example.com") == "check this"


def test_remove_http_urls():
    assert clean_tweet("Visit http://x.com now") == "visit now"


def test_remove_multiple_mentions():
    assert clean_tweet("@alice @bob hello") == "hello"


def test_normalize_whitespace():
    assert clean_tweet("hello   world  ") == "hello world"


def test_lowercase_normalization():
    assert clean_tweet("THIS IS LOUD") == "this is loud"


def test_empty_tweet():
    assert clean_tweet("") == ""


def test_mixed_content():
    text = "@user Check https://t.co/abcde this is great!"
    result = clean_tweet(text)
    assert "@" not in result
    assert "http" not in result
    assert "great" in result


def test_newlines_removed():
    assert clean_tweet("hello\n\nworld") == "hello world"


def test_only_mention_and_url():
    assert clean_tweet("@user https://x.com") == ""
