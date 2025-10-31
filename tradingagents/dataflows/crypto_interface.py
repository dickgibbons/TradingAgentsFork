"""
Crypto Data Interface for Trading Agents
LangChain-compatible tool functions for cryptocurrency analysis
"""

from typing import Annotated

try:
    # Try relative imports (when used as module)
    from .coingecko_utils import CoinGeckoUtils
    from .onchain_utils import OnChainUtils
    from .cryptonews_utils import CryptoNewsUtils
except ImportError:
    # Fall back to direct imports (when testing standalone)
    from coingecko_utils import CoinGeckoUtils
    from onchain_utils import OnChainUtils
    from cryptonews_utils import CryptoNewsUtils


# Initialize utility classes (shared across all function calls)
_coingecko = CoinGeckoUtils()
_onchain = OnChainUtils()
_cryptonews = CryptoNewsUtils()


# ==================== PRICE & MARKET DATA TOOLS ====================

def get_crypto_price_data(
    symbol: Annotated[str, "Crypto symbol (e.g., 'BTC', 'ETH', 'SOL')"],
    days: Annotated[int, "Number of days of historical price data"] = 90,
) -> str:
    """
    Get cryptocurrency price history (OHLCV data) and current market statistics.

    This tool provides comprehensive price and market data including:
    - Historical OHLCV (Open, High, Low, Close, Volume) candles
    - Current price and 24h/7d/30d price changes
    - Market cap, trading volume, and market cap rank
    - Circulating supply, total supply, max supply
    - All-time high/low prices and dates

    Args:
        symbol: Cryptocurrency symbol (BTC, ETH, SOL, MATIC, etc.)
        days: Number of days of historical data (default: 90)

    Returns:
        Formatted string with market data and price history summary

    Example:
        get_crypto_price_data("BTC", 30) returns Bitcoin data for last 30 days
    """
    try:
        # Get current market data
        market_summary = _coingecko.get_market_data_summary(symbol)

        # Get price history
        price_df = _coingecko.get_price_history(symbol, days=days)

        if price_df.empty:
            return f"Could not fetch price data for {symbol}"

        # Create price history summary
        recent_price = price_df.iloc[-1]['close'] if not price_df.empty else 0
        price_change = ((price_df.iloc[-1]['close'] - price_df.iloc[0]['close']) / price_df.iloc[0]['close'] * 100) if len(price_df) > 0 else 0

        price_history_summary = f"""
Price History ({days} days):
  Current: ${recent_price:,.2f}
  Change: {price_change:+.2f}%
  High: ${price_df['high'].max():,.2f}
  Low: ${price_df['low'].min():,.2f}
  Avg Volume: ${price_df['volume'].mean():,.0f}
"""

        return market_summary + "\n" + price_history_summary

    except Exception as e:
        return f"Error fetching price data for {symbol}: {str(e)}"


def get_global_crypto_market(
) -> str:
    """
    Get global cryptocurrency market overview.

    This tool provides macro-level market intelligence including:
    - Total crypto market capitalization
    - 24-hour market cap change percentage
    - Total 24-hour trading volume
    - Bitcoin and Ethereum market dominance percentages
    - Number of active cryptocurrencies
    - Fear & Greed Index (market sentiment indicator)

    Returns:
        Formatted string with global market statistics

    Use this to understand overall market conditions before analyzing specific coins.
    """
    try:
        return _coingecko.get_global_market_summary()
    except Exception as e:
        return f"Error fetching global market data: {str(e)}"


def get_crypto_fear_greed_index(
) -> str:
    """
    Get the Crypto Fear & Greed Index (0-100 scale).

    The Fear & Greed Index analyzes market sentiment from multiple sources:
    - Volatility (25%)
    - Market momentum/volume (25%)
    - Social media sentiment (15%)
    - Surveys (15%)
    - Bitcoin dominance (10%)
    - Google Trends (10%)

    Scale:
    - 0-24: Extreme Fear (potential buying opportunity)
    - 25-49: Fear
    - 50-74: Greed
    - 75-100: Extreme Greed (potential market top)

    Returns:
        Formatted string with current index value and classification
    """
    try:
        fear_greed = _coingecko.get_fear_greed_index()

        return f"""
=== Crypto Fear & Greed Index ===

Current Value: {fear_greed['value']}/100
Classification: {fear_greed['value_classification']}

Interpretation:
- This index measures market sentiment on a 0-100 scale
- Current reading suggests: {fear_greed['value_classification']} market conditions
"""
    except Exception as e:
        return f"Error fetching Fear & Greed Index: {str(e)}"


def get_trending_cryptocurrencies(
    limit: Annotated[int, "Number of trending coins to return"] = 10,
) -> str:
    """
    Get currently trending cryptocurrencies based on search interest and social activity.

    This identifies coins experiencing surge in attention across:
    - Search volume spikes
    - Social media mentions
    - Price momentum

    Useful for identifying emerging narratives or potential volatility.

    Args:
        limit: Number of trending coins to return (default: 10)

    Returns:
        Formatted list of trending cryptocurrencies with basic info
    """
    try:
        trending = _coingecko.get_trending_coins(limit=limit)

        if not trending:
            return "No trending coins data available"

        result = f"=== Top {len(trending)} Trending Cryptocurrencies ===\n\n"

        for i, coin in enumerate(trending, 1):
            result += f"{i}. {coin['name']} ({coin['symbol']})\n"
            result += f"   Market Cap Rank: #{coin['market_cap_rank']}\n"
            result += f"   Price (BTC): {coin['price_btc']:.8f} BTC\n\n"

        return result

    except Exception as e:
        return f"Error fetching trending coins: {str(e)}"


# ==================== ON-CHAIN DATA TOOLS ====================

def get_bitcoin_onchain_metrics(
) -> str:
    """
    Get Bitcoin blockchain metrics and network health indicators.

    Provides critical on-chain data including:
    - Network hash rate (mining power/security)
    - Mining difficulty
    - Average block time
    - Total BTC mined (circulating supply)
    - 24h transaction count and volume
    - Mempool size and congestion level
    - Large transaction alerts (whale movements)
    - Miner revenue

    Returns:
        Formatted string with Bitcoin on-chain analytics

    Use this to assess Bitcoin network health and detect unusual activity.
    """
    try:
        return _onchain.get_bitcoin_onchain_summary()
    except Exception as e:
        return f"Error fetching Bitcoin on-chain data: {str(e)}"


def get_ethereum_onchain_metrics(
) -> str:
    """
    Get Ethereum blockchain metrics and network activity.

    Provides Ethereum-specific data including:
    - Gas prices (safe, standard, fast in Gwei)
    - Base fee (EIP-1559)
    - Network congestion level
    - Total ETH supply
    - ETH2 staking statistics

    Returns:
        Formatted string with Ethereum on-chain analytics

    Important for understanding Ethereum transaction costs and network usage.
    Note: Requires ETHERSCAN_API_KEY environment variable.
    """
    try:
        return _onchain.get_ethereum_onchain_summary()
    except Exception as e:
        return f"Error fetching Ethereum on-chain data: {str(e)}"


def get_onchain_metrics(
    symbol: Annotated[str, "Crypto symbol (e.g., 'BTC', 'ETH', 'SOL')"],
) -> str:
    """
    Get on-chain metrics for any cryptocurrency.

    Routes to specialized on-chain data based on the cryptocurrency:
    - Bitcoin: Network hash rate, mempool, whale transactions
    - Ethereum: Gas prices, network congestion, staking
    - Others: Social metrics, GitHub activity (when available)

    Args:
        symbol: Cryptocurrency symbol

    Returns:
        Formatted string with relevant on-chain metrics
    """
    try:
        return _onchain.get_general_onchain_summary(symbol)
    except Exception as e:
        return f"Error fetching on-chain metrics for {symbol}: {str(e)}"


# ==================== NEWS & SENTIMENT TOOLS ====================

def get_crypto_news(
    symbol: Annotated[str, "Crypto symbol to filter news (optional)"] = None,
    hours: Annotated[int, "Hours to look back for news"] = 24,
    max_articles: Annotated[int, "Maximum number of articles to return"] = 10,
) -> str:
    """
    Get latest cryptocurrency news from multiple trusted sources.

    Aggregates news from:
    - CoinTelegraph (major crypto news)
    - Decrypt (tech-focused crypto coverage)
    - CoinDesk (financial crypto news)
    - The Block (research & analysis)
    - Bitcoin Magazine (BTC-specific, if symbol=BTC)

    Args:
        symbol: Filter to specific cryptocurrency (e.g., "BTC", "ETH"), or None for general crypto news
        hours: How many hours back to fetch news (default: 24)
        max_articles: Maximum articles to include (default: 10)

    Returns:
        Formatted news summary with titles, sources, links, and snippets

    Use this to stay informed on market-moving events and narratives.
    """
    try:
        return _cryptonews.get_crypto_news_summary(
            symbol=symbol,
            hours=hours,
            max_articles=max_articles
        )
    except Exception as e:
        return f"Error fetching crypto news: {str(e)}"


def get_regulatory_news(
) -> str:
    """
    Get recent regulatory and legal news affecting cryptocurrencies.

    Filters for news containing keywords like:
    - SEC, CFTC, regulatory, regulation
    - ETF approvals/denials
    - Legal actions, lawsuits
    - Government policy, legislation
    - Compliance requirements

    Returns:
        Formatted summary of regulatory developments from the past week

    Critical for understanding regulatory risks and opportunities.
    """
    try:
        reg_news = _cryptonews.get_regulatory_news(hours=168)  # Last 7 days

        if not reg_news:
            return "No significant regulatory news in the past week"

        result = "=== Recent Regulatory News (Last 7 Days) ===\n\n"

        for i, article in enumerate(reg_news[:10], 1):
            result += f"{i}. {article['title']}\n"
            result += f"   Source: {article['source']}"

            if article.get('published_at'):
                result += f" | {article['published_at'][:16]}"

            result += f"\n   {article['url']}\n\n"

        return result

    except Exception as e:
        return f"Error fetching regulatory news: {str(e)}"


# ==================== COMBINED ANALYSIS TOOLS ====================

def get_crypto_full_analysis(
    symbol: Annotated[str, "Crypto symbol to analyze (e.g., 'BTC', 'ETH')"],
    days: Annotated[int, "Days of price history"] = 30,
) -> str:
    """
    Get comprehensive analysis combining price, on-chain, and news data.

    This is a convenience tool that provides a complete picture by combining:
    - Current price and market data
    - Price history over specified period
    - On-chain metrics (if available for this crypto)
    - Recent news (last 48 hours)
    - Global market context

    Args:
        symbol: Cryptocurrency to analyze
        days: Days of price history to include

    Returns:
        Comprehensive formatted analysis report

    Use this as a starting point for deep analysis of a specific cryptocurrency.
    """
    try:
        sections = []

        # Price & Market Data
        sections.append(get_crypto_price_data(symbol, days))

        # On-Chain Metrics
        sections.append("\n" + "="*80)
        sections.append(get_onchain_metrics(symbol))

        # Recent News
        sections.append("\n" + "="*80)
        sections.append(get_crypto_news(symbol=symbol, hours=48, max_articles=5))

        # Global Market Context
        sections.append("\n" + "="*80)
        sections.append(get_global_crypto_market())

        return "\n".join(sections)

    except Exception as e:
        return f"Error generating full analysis for {symbol}: {str(e)}"


# ==================== TOOL REGISTRY ====================

# List of all available crypto tools for easy reference
CRYPTO_TOOLS = [
    get_crypto_price_data,
    get_global_crypto_market,
    get_crypto_fear_greed_index,
    get_trending_cryptocurrencies,
    get_bitcoin_onchain_metrics,
    get_ethereum_onchain_metrics,
    get_onchain_metrics,
    get_crypto_news,
    get_regulatory_news,
    get_crypto_full_analysis,
]


# Tool categories for organized access
MARKET_DATA_TOOLS = [
    get_crypto_price_data,
    get_global_crypto_market,
    get_crypto_fear_greed_index,
    get_trending_cryptocurrencies,
]

ONCHAIN_TOOLS = [
    get_bitcoin_onchain_metrics,
    get_ethereum_onchain_metrics,
    get_onchain_metrics,
]

NEWS_TOOLS = [
    get_crypto_news,
    get_regulatory_news,
]

ANALYSIS_TOOLS = [
    get_crypto_full_analysis,
]
