"""Test suite for src/crawler/rate_limiter.py"""
import time
import pytest
from src.crawler.rate_limiter import RateLimiter


def test_rate_limiter_wait_blocks():
    limiter = RateLimiter(delay=0.1)
    start = time.time()
    limiter.wait()
    elapsed = time.time() - start
    assert elapsed >= 0.09


def test_rate_limiter_consecutive_delays():
    limiter = RateLimiter(delay=0.05)
    start = time.time()
    limiter.wait()
    limiter.wait()
    elapsed = time.time() - start
    assert elapsed >= 0.09


def test_rate_limiter_exponential_backoff():
    limiter = RateLimiter(delay=0.1, backoff_factor=2.0)
    limiter.trigger_backoff()
    assert limiter.current_delay == 0.2
    limiter.trigger_backoff()
    assert limiter.current_delay == 0.4


def test_rate_limiter_reset():
    limiter = RateLimiter(delay=0.5)
    limiter.trigger_backoff()
    limiter.trigger_backoff()
    limiter.reset()
    assert limiter.current_delay == 0.5
    assert limiter.retry_count == 0


def test_rate_limiter_should_retry():
    limiter = RateLimiter(delay=1.0, max_retries=3)
    assert limiter.should_retry() is True
    limiter.trigger_backoff()
    limiter.trigger_backoff()
    limiter.trigger_backoff()
    assert limiter.should_retry() is False


def test_rate_limiter_remaining_retries():
    limiter = RateLimiter(delay=1.0, max_retries=3)
    assert limiter.remaining_retries == 3
    limiter.trigger_backoff()
    assert limiter.remaining_retries == 2
