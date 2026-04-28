import time
from typing import Optional


class RateLimiter:
    """
    Rate limiter with delay between actions and exponential backoff.
    """

    def __init__(self, delay: float = 2.0, max_retries: int = 3, backoff_factor: float = 2.0):
        self.base_delay = delay
        self.current_delay = delay
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_count = 0

    def wait(self) -> None:
        """Wait for the current delay duration."""
        time.sleep(self.current_delay)

    def trigger_backoff(self) -> None:
        """Double the delay (exponential backoff), capped at 60s."""
        self.current_delay = min(self.current_delay * self.backoff_factor, 60.0)
        self.retry_count += 1

    def reset(self) -> None:
        """Reset delay to base and clear retry count."""
        self.current_delay = self.base_delay
        self.retry_count = 0

    def should_retry(self) -> bool:
        """Return True if retries are still available."""
        return self.retry_count < self.max_retries

    @property
    def remaining_retries(self) -> int:
        return self.max_retries - self.retry_count