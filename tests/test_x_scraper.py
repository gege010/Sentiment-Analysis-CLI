"""Test suite for src/crawler/x_scraper.py"""
import pytest
from unittest.mock import MagicMock, patch
from src.crawler.x_scraper import XScraper


def test_xscraper_build_search_url():
    scraper = XScraper(username="test", password="pass")
    url = scraper._build_search_url("AI Technology")
    assert "AI%2BTechnology" in url or "AI+Technology" in url
    assert "f=live" in url


def test_xscraper_build_search_url_handles_ampersand():
    scraper = XScraper(username="test", password="pass")
    url = scraper._build_search_url("AI & ML news")
    assert "%26" in url or "&" not in url.split("f=live")[0].split("q=")[1]


def test_xscraper_initial_state():
    scraper = XScraper(username="u", password="p")
    assert scraper.username == "u"
    assert scraper.password == "p"
    assert scraper.tweet_count == 200


def test_xscraper_custom_tweet_count():
    scraper = XScraper(username="u", password="p", tweet_count=100)
    assert scraper.tweet_count == 100


def test_xscraper_search_url_contains_topic():
    scraper = XScraper(username="test", password="pass")
    url = scraper._build_search_url("machine learning")
    assert "machine" in url
    assert "learning" in url


def test_xscraper_limiter_is_rate_limiter():
    scraper = XScraper(username="u", password="p")
    from src.crawler.rate_limiter import RateLimiter
    assert isinstance(scraper.limiter, RateLimiter)
