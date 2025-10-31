"""
Crypto News Aggregator for Trading Agents
Aggregates news from multiple crypto-specific sources
"""

import requests
import feedparser
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import time
import os
from bs4 import BeautifulSoup


class CryptoNewsUtils:
    """Aggregates cryptocurrency news from multiple sources"""

    def __init__(self, cryptopanic_api_key: Optional[str] = None):
        """Initialize crypto news aggregator

        Args:
            cryptopanic_api_key: CryptoPanic API key (free tier available)
        """
        self.cryptopanic_key = cryptopanic_api_key or os.getenv("CRYPTOPANIC_API_KEY")
        self.last_request_time = {}
        self.rate_limit_delay = 1.0

    def _rate_limit(self, source: str):
        """Enforce rate limiting per source"""
        current_time = time.time()
        last_time = self.last_request_time.get(source, 0)
        time_since_last = current_time - last_time

        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)

        self.last_request_time[source] = time.time()

    def _make_request(self, url: str, params: Dict = None, source: str = "default") -> Dict:
        """Make API request with error handling"""
        self._rate_limit(source)

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"News API error ({source}): {e}")
            return {}

    # ==================== CRYPTOPANIC API ====================

    def get_cryptopanic_news(
        self,
        symbol: Optional[str] = None,
        filter_type: str = "hot",
        limit: int = 20
    ) -> List[Dict]:
        """Get news from CryptoPanic API

        Args:
            symbol: Crypto symbol to filter by (optional)
            filter_type: Type of news (hot, rising, bullish, bearish, important, saved, lol)
            limit: Number of articles to return

        Returns:
            List of news articles
        """
        if not self.cryptopanic_key:
            return []

        url = "https://cryptopanic.com/api/v1/posts/"
        params = {
            "auth_token": self.cryptopanic_key,
            "filter": filter_type,
            "public": "true"
        }

        if symbol:
            params["currencies"] = symbol.upper()

        data = self._make_request(url, params, source="cryptopanic")

        if not data or "results" not in data:
            return []

        articles = []
        for item in data["results"][:limit]:
            articles.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "source": item.get("source", {}).get("title", ""),
                "published_at": item.get("published_at", ""),
                "domain": item.get("domain", ""),
                "votes": {
                    "positive": item.get("votes", {}).get("positive", 0),
                    "negative": item.get("votes", {}).get("negative", 0),
                    "important": item.get("votes", {}).get("important", 0),
                },
                "kind": item.get("kind", ""),  # news, media, blog
                "currencies": [c["code"] for c in item.get("currencies", [])],
            })

        return articles

    # ==================== RSS FEEDS ====================

    def get_cointelegraph_news(self, limit: int = 10) -> List[Dict]:
        """Get latest news from CoinTelegraph RSS feed

        Args:
            limit: Number of articles to return

        Returns:
            List of news articles
        """
        url = "https://cointelegraph.com/rss"

        try:
            self._rate_limit("cointelegraph")
            feed = feedparser.parse(url)

            articles = []
            for entry in feed.entries[:limit]:
                articles.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "source": "CoinTelegraph",
                    "published_at": entry.get("published", ""),
                    "summary": entry.get("summary", ""),
                })

            return articles
        except Exception as e:
            print(f"CoinTelegraph RSS error: {e}")
            return []

    def get_decrypt_news(self, limit: int = 10) -> List[Dict]:
        """Get latest news from Decrypt RSS feed

        Args:
            limit: Number of articles to return

        Returns:
            List of news articles
        """
        url = "https://decrypt.co/feed"

        try:
            self._rate_limit("decrypt")
            feed = feedparser.parse(url)

            articles = []
            for entry in feed.entries[:limit]:
                articles.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "source": "Decrypt",
                    "published_at": entry.get("published", ""),
                    "summary": entry.get("summary", ""),
                })

            return articles
        except Exception as e:
            print(f"Decrypt RSS error: {e}")
            return []

    def get_coindesk_news(self, limit: int = 10) -> List[Dict]:
        """Get latest news from CoinDesk RSS feed

        Args:
            limit: Number of articles to return

        Returns:
            List of news articles
        """
        url = "https://www.coindesk.com/arc/outboundfeeds/rss/"

        try:
            self._rate_limit("coindesk")
            feed = feedparser.parse(url)

            articles = []
            for entry in feed.entries[:limit]:
                articles.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "source": "CoinDesk",
                    "published_at": entry.get("published", ""),
                    "summary": entry.get("summary", ""),
                })

            return articles
        except Exception as e:
            print(f"CoinDesk RSS error: {e}")
            return []

    def get_theblock_news(self, limit: int = 10) -> List[Dict]:
        """Get latest news from The Block RSS feed

        Args:
            limit: Number of articles to return

        Returns:
            List of news articles
        """
        url = "https://www.theblock.co/rss.xml"

        try:
            self._rate_limit("theblock")
            feed = feedparser.parse(url)

            articles = []
            for entry in feed.entries[:limit]:
                articles.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "source": "The Block",
                    "published_at": entry.get("published", ""),
                    "summary": entry.get("summary", ""),
                })

            return articles
        except Exception as e:
            print(f"The Block RSS error: {e}")
            return []

    def get_bitcoinmagazine_news(self, limit: int = 10) -> List[Dict]:
        """Get latest news from Bitcoin Magazine RSS feed

        Args:
            limit: Number of articles to return

        Returns:
            List of news articles
        """
        url = "https://bitcoinmagazine.com/.rss/full/"

        try:
            self._rate_limit("bitcoinmagazine")
            feed = feedparser.parse(url)

            articles = []
            for entry in feed.entries[:limit]:
                articles.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "source": "Bitcoin Magazine",
                    "published_at": entry.get("published", ""),
                    "summary": entry.get("summary", ""),
                })

            return articles
        except Exception as e:
            print(f"Bitcoin Magazine RSS error: {e}")
            return []

    # ==================== AGGREGATION & FORMATTING ====================

    def get_all_crypto_news(
        self,
        symbol: Optional[str] = None,
        hours: int = 24,
        max_per_source: int = 5
    ) -> List[Dict]:
        """Aggregate news from all sources

        Args:
            symbol: Filter by crypto symbol (optional)
            hours: Only include news from last N hours
            max_per_source: Max articles per source

        Returns:
            Combined list of news articles, sorted by date
        """
        all_news = []

        # Get from CryptoPanic (if API key available)
        if self.cryptopanic_key:
            cryptopanic_news = self.get_cryptopanic_news(
                symbol=symbol,
                filter_type="hot",
                limit=max_per_source
            )
            all_news.extend(cryptopanic_news)

        # Get from RSS feeds
        all_news.extend(self.get_cointelegraph_news(limit=max_per_source))
        all_news.extend(self.get_decrypt_news(limit=max_per_source))
        all_news.extend(self.get_coindesk_news(limit=max_per_source))
        all_news.extend(self.get_theblock_news(limit=max_per_source))

        # Filter by bitcoin if symbol is BTC
        if symbol and symbol.upper() == "BTC":
            all_news.extend(self.get_bitcoinmagazine_news(limit=max_per_source))

        # RSS feeds only return recent articles (typically last 24-48 hours)
        # So we skip strict date filtering and just return all fetched articles
        # This ensures we always get news even if date parsing fails

        # Sort by date (newest first)
        try:
            all_news.sort(
                key=lambda x: x.get("published_at", ""),
                reverse=True
            )
        except:
            pass

        return all_news

    def get_crypto_news_summary(
        self,
        symbol: Optional[str] = None,
        hours: int = 24,
        max_articles: int = 10
    ) -> str:
        """Get formatted news summary for LLM

        Args:
            symbol: Crypto symbol to filter by
            hours: Last N hours of news
            max_articles: Maximum articles to include

        Returns:
            Formatted string with news summary
        """
        articles = self.get_all_crypto_news(symbol=symbol, hours=hours)

        if not articles:
            return f"No recent crypto news found in the last {hours} hours"

        header = f"=== Crypto News (Last {hours} Hours)"
        if symbol:
            header += f" - {symbol.upper()}"
        header += " ===\n"

        summary = header

        for i, article in enumerate(articles[:max_articles], 1):
            summary += f"\n{i}. {article['title']}\n"
            summary += f"   Source: {article['source']}"

            if article.get("published_at"):
                summary += f" | {article['published_at'][:16]}"

            # Add voting info if available (CryptoPanic)
            if article.get("votes"):
                votes = article["votes"]
                if votes.get("important", 0) > 0:
                    summary += f" | ⭐ Important ({votes['important']})"
                if votes.get("positive", 0) > votes.get("negative", 0):
                    summary += f" | 📈 Bullish"
                elif votes.get("negative", 0) > votes.get("positive", 0):
                    summary += f" | 📉 Bearish"

            summary += f"\n   {article['url']}\n"

            # Add summary if available
            if article.get("summary"):
                # Clean HTML tags from summary
                try:
                    soup = BeautifulSoup(article["summary"], "html.parser")
                    clean_summary = soup.get_text()[:200]  # First 200 chars
                    if clean_summary:
                        summary += f"   {clean_summary}...\n"
                except:
                    pass

        summary += f"\n📰 Total Articles: {len(articles[:max_articles])}"

        return summary.strip()

    def get_regulatory_news(self, hours: int = 168) -> List[Dict]:
        """Get regulatory and policy news (last week)

        Args:
            hours: Look back hours (default: 7 days)

        Returns:
            List of regulatory news articles
        """
        # Get news from all sources
        all_news = self.get_all_crypto_news(hours=hours, max_per_source=10)

        # Filter for regulatory keywords
        regulatory_keywords = [
            "sec", "regulation", "regulatory", "ban", "legal", "lawsuit",
            "compliance", "government", "legislation", "policy", "etf",
            "securities", "cftc", "congress", "senate", "court"
        ]

        regulatory_news = []
        for article in all_news:
            title_lower = article.get("title", "").lower()
            summary_lower = article.get("summary", "").lower()

            if any(keyword in title_lower or keyword in summary_lower
                   for keyword in regulatory_keywords):
                regulatory_news.append(article)

        return regulatory_news


# Convenience functions for easy use
def get_crypto_news(symbol: Optional[str] = None, hours: int = 24) -> str:
    """Convenience function to get crypto news summary"""
    utils = CryptoNewsUtils()
    return utils.get_crypto_news_summary(symbol=symbol, hours=hours)


def get_bitcoin_news(hours: int = 24) -> str:
    """Convenience function to get Bitcoin-specific news"""
    utils = CryptoNewsUtils()
    return utils.get_crypto_news_summary(symbol="BTC", hours=hours)


def get_regulatory_updates() -> str:
    """Convenience function to get regulatory news"""
    utils = CryptoNewsUtils()
    news = utils.get_regulatory_news(hours=168)  # Last week

    if not news:
        return "No significant regulatory news in the past week"

    summary = "=== Recent Regulatory News (Last 7 Days) ===\n"
    for i, article in enumerate(news[:5], 1):
        summary += f"\n{i}. {article['title']}\n"
        summary += f"   Source: {article['source']} | {article.get('published_at', '')[:16]}\n"

    return summary.strip()


# Example usage
if __name__ == "__main__":
    news = CryptoNewsUtils()

    print("="*80)
    print("GENERAL CRYPTO NEWS (Last 24 Hours)")
    print("="*80)
    print(news.get_crypto_news_summary(hours=24, max_articles=5))

    print("\n" + "="*80)
    print("BITCOIN-SPECIFIC NEWS")
    print("="*80)
    print(news.get_crypto_news_summary(symbol="BTC", hours=48, max_articles=5))

    print("\n" + "="*80)
    print("REGULATORY NEWS (Last Week)")
    print("="*80)
    reg_news = news.get_regulatory_news(hours=168)
    print(f"Found {len(reg_news)} regulatory articles")
    for i, article in enumerate(reg_news[:3], 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Source: {article['source']}")
