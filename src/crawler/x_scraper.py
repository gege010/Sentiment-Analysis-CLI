import re
import time
import random
from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import quote
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
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
    Supports two authentication modes:
    1. Cookie-based (recommended) - uses cookies from .env
    2. Password-based - uses username/password credentials

    To use cookie-based auth:
    1. Export cookies from Chrome (after logging into X.com)
    2. Add cookies to .env file:
       X_COOKIE_AUTH_TOKEN=your_auth_token
       X_COOKIE_CT0=your_ct0_token
       X_COOKIE_GUEST_ID=your_guest_id
    3. Or use python scripts/export_cookies.py --save
    """

    BASE_URL = "https://x.com"
    SEARCH_URL_TEMPLATE = "https://x.com/search?q={query}&f=live"

    # Realistic user agents for stealth mode
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    ]

    # Cookie names to extract from X.com
    COOKIE_NAMES = [
        'auth_token', 'ct0', 'guest_id', '_twitter_sess',
        'kdt', 'twid', 'att', 'external_referer'
    ]

    def __init__(
        self,
        username: str = "",
        password: str = "",
        headless: bool = True,
        tweet_count: int = 200,
        cookies: dict = None,
    ):
        self.username = username
        self.password = password
        self.headless = headless
        self.tweet_count = tweet_count
        self.cookies = cookies or {}
        self.limiter = RateLimiter(delay=2.0, max_retries=3)

    def _create_context_with_cookies(self, pw) -> BrowserContext:
        """Create browser context with cookies from .env."""
        ua = random.choice(self.USER_AGENTS)

        context = pw.chromium.launch_persistent_context(
            user_data_dir=None,  # Fresh context each time
            headless=self.headless,
            viewport={"width": 1920, "height": 1080},
            user_agent=ua,
        )

        # Add cookies to context
        cookies = []
        for name, value in self.cookies.items():
            cookies.append({
                'name': name,
                'value': value,
                'domain': '.x.com',
                'path': '/',
            })

        if cookies:
            context.add_cookies(cookies)

        # Inject stealth script
        page = context.new_page()
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = { runtime: {} };
            delete navigator.__proto__['webdriver'];
        """)
        page.close()

        return context

    def scrape(self, topic: str) -> ScrapeResult:
        """
        Main entry point. Scrape tweets for topic using cookie auth.
        """
        tweets: List[Tweet] = []
        pw = None
        browser = None

        try:
            # Import here to ensure fresh import each time
            from playwright.sync_api import sync_playwright

            pw = sync_playwright().start()
            browser = pw.chromium.launch(headless=self.headless)

            # Create context with cookies
            context = self._create_context_with_cookies(pw)

            # Get or create page
            page = context.new_page() if not context.pages else context.pages[0]

            # Navigate directly to search (cookies handle auth)
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
            if pw:
                try:
                    pw.stop()
                except Exception:
                    pass

        return ScrapeResult(tweets=tweets, topic=topic, total=len(tweets))

    def _build_search_url(self, topic: str) -> str:
        """Build X.com search URL for topic."""
        encoded = quote(topic, safe="")
        return f"{self.BASE_URL}/search?q={encoded}&f=live"

    def _wait_for_results(self, page: Page) -> None:
        """Wait for search results to load."""
        try:
            page.wait_for_selector('article[data-testid="tweet"]', timeout=20000)
        except Exception:
            raise XScrapeError("No tweets found. X.com may be blocking the request.")
        self.limiter.wait()

    def _scroll_and_scrape(self, page: Page) -> List[Tweet]:
        """Scroll page, load more tweets, extract data."""
        tweets: List[Tweet] = []
        seen_ids: set = set()
        scroll_attempts = 0
        max_attempts = 30  # Increased from 10
        last_tweet_count = 0
        stuck_count = 0  # Track if we're stuck (no new tweets)

        while len(tweets) < self.tweet_count and scroll_attempts < max_attempts:
            article_elements = page.query_selector_all('article[data-testid="tweet"]')
            new_tweets_this_scroll = 0

            for article in article_elements:
                tweet = self._extract_tweet(article)
                if tweet and tweet.id not in seen_ids:
                    seen_ids.add(tweet.id)
                    tweets.append(tweet)
                    new_tweets_this_scroll += 1
                    if len(tweets) >= self.tweet_count:
                        break

            # Check if we're stuck (no new tweets found)
            if new_tweets_this_scroll == 0:
                stuck_count += 1
                if stuck_count >= 5:  # If stuck 5 times, stop scrolling
                    break
            else:
                stuck_count = 0

            if len(tweets) >= self.tweet_count:
                break

            # Scroll down to load more (full page scroll)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(random.uniform(2000, 3000))
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