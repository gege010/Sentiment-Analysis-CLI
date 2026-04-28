import re
from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import quote
from playwright.sync_api import sync_playwright, Page, Browser
from src.crawler.rate_limiter import RateLimiter


@dataclass
class Tweet:
    id: str
    text: str
    username: str
    timestamp: str
    likes: int = 0
    retweets: int = 0


@dataclass
class ScrapeResult:
    tweets: List[Tweet]
    topic: str
    total: int


class XScraper:
    """
    Scrapes tweets from X.com using Playwright.
    Handles login, navigation to search, scrolling, and tweet extraction.
    """

    BASE_URL = "https://x.com"
    SEARCH_URL_TEMPLATE = "https://x.com/search?q={query}&f=live"

    def __init__(
        self,
        username: str,
        password: str,
        headless: bool = True,
        tweet_count: int = 200,
    ):
        self.username = username
        self.password = password
        self.headless = headless
        self.tweet_count = tweet_count
        self.limiter = RateLimiter(delay=2.0, max_retries=3)

    def scrape(self, topic: str) -> ScrapeResult:
        """
        Main entry point. Login to X, scrape tweets for topic, return results.
        """
        tweets: List[Tweet] = []
        browser: Optional[Browser] = None

        try:
            pw = sync_playwright().start()
            browser = pw.chromium.launch(headless=self.headless)
            context = browser.new_context()
            page = context.new_page()

            self._login(page)
            search_url = self._build_search_url(topic)
            page.goto(search_url)
            self._wait_for_results(page)

            tweets = self._scroll_and_scrape(page)
            self.limiter.reset()

        except Exception as e:
            raise XScrapeError(f"Scraping failed: {e}") from e

        finally:
            if browser:
                browser.close()

        return ScrapeResult(tweets=tweets, topic=topic, total=len(tweets))

    def _login(self, page: Page) -> None:
        """Navigate to login page and authenticate."""
        page.goto(f"{self.BASE_URL}/login")
        page.wait_for_load_state("networkidle")

        # Fill email/username
        page.fill('input[name="text"]', self.username)
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

        # Fill password
        page.fill('input[name="password"]', self.password)
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")

    def _build_search_url(self, topic: str) -> str:
        """Build X.com search URL for topic."""
        encoded = quote(topic, safe="")
        return f"{self.BASE_URL}/search?q={encoded}&f=live"

    def _wait_for_results(self, page: Page) -> None:
        """Wait for search results to load."""
        page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)
        self.limiter.wait()

    def _scroll_and_scrape(self, page: Page) -> List[Tweet]:
        """Scroll page, load more tweets, extract data."""
        tweets: List[Tweet] = []
        seen_ids: set = set()
        scroll_attempts = 0
        max_attempts = 10

        while len(tweets) < self.tweet_count and scroll_attempts < max_attempts:
            article_elements = page.query_selector_all('article[data-testid="tweet"]')

            for article in article_elements:
                tweet = self._extract_tweet(article)
                if tweet and tweet.id not in seen_ids:
                    seen_ids.add(tweet.id)
                    tweets.append(tweet)
                    if len(tweets) >= self.tweet_count:
                        break

            if len(tweets) >= self.tweet_count:
                break

            # Scroll down to load more
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1500)
            scroll_attempts += 1
            self.limiter.wait()

        return tweets

    def _extract_tweet(self, article) -> Optional[Tweet]:
        """Extract tweet data from an article element."""
        try:
            # Text content
            text_elem = article.query_selector('div[data-testid="tweetText"]')
            text = text_elem.inner_text() if text_elem else ""

            # Username
            user_elem = article.query_selector('a[role="link"]')
            username = ""
            if user_elem:
                href = user_elem.get_attribute("href") or ""
                username = "@" + href.lstrip("/")

            # Timestamp
            time_elem = article.query_selector("time")
            timestamp = time_elem.get_attribute("datetime") if time_elem else ""

            # Tweet ID from article data attributes or URL
            link_elem = article.query_selector('a[href*="/status/"]')
            tweet_id = ""
            if link_elem:
                href = link_elem.get_attribute("href") or ""
                match = re.search(r"/status/(\d+)", href)
                if match:
                    tweet_id = match.group(1)

            return Tweet(
                id=tweet_id,
                text=text,
                username=username,
                timestamp=timestamp,
            )

        except Exception:
            return None


class XScrapeError(Exception):
    """Raised when X scraping fails."""
    pass