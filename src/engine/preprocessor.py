import re

URL_PATTERN = re.compile(r"https?://\S+")
MENTION_PATTERN = re.compile(r"@\w+")
WHITESPACE_PATTERN = re.compile(r"\s+")


def clean_tweet(text: str) -> str:
    """
    Clean tweet text for sentiment analysis:
    - Remove @mentions
    - Remove URLs (http:// and https://)
    - Normalize whitespace to single space
    - Lowercase for consistency
    """
    if not text:
        return ""

    # Remove URLs
    text = URL_PATTERN.sub("", text)

    # Remove mentions
    text = MENTION_PATTERN.sub("", text)

    # Normalize whitespace
    text = WHITESPACE_PATTERN.sub(" ", text)

    # Strip and lower
    text = text.strip().lower()

    return text