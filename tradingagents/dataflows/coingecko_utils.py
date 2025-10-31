"""
CoinGecko API Utilities for Crypto Trading Agents
Provides cryptocurrency price, market, and historical data
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import time
import os


class CoinGeckoUtils:
    """Wrapper for CoinGecko API with rate limiting and error handling"""

    BASE_URL = "https://api.coingecko.com/api/v3"

    # Common crypto symbol to CoinGecko ID mapping
    SYMBOL_TO_ID = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "MATIC": "matic-network",
        "AVAX": "avalanche-2",
        "BNB": "binancecoin",
        "ADA": "cardano",
        "DOT": "polkadot",
        "LINK": "chainlink",
        "UNI": "uniswap",
        "ATOM": "cosmos",
        "XRP": "ripple",
        "DOGE": "dogecoin",
        "SHIB": "shiba-inu",
        "LTC": "litecoin",
        "BCH": "bitcoin-cash",
        "NEAR": "near",
        "APT": "aptos",
        "ARB": "arbitrum",
        "OP": "optimism",
    }

    def __init__(self, api_key: Optional[str] = None):
        """Initialize CoinGecko client

        Args:
            api_key: Optional API key for higher rate limits
        """
        self.api_key = api_key or os.getenv("COINGECKO_API_KEY")
        self.last_request_time = 0
        self.rate_limit_delay = 1.2  # Seconds between requests (free tier: 50 calls/min)

    def _rate_limit(self):
        """Enforce rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last_request)

        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request with error handling

        Args:
            endpoint: API endpoint (e.g., "/coins/bitcoin")
            params: Query parameters

        Returns:
            JSON response as dict
        """
        self._rate_limit()

        url = f"{self.BASE_URL}{endpoint}"
        headers = {}

        if self.api_key:
            headers["x-cg-pro-api-key"] = self.api_key

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"CoinGecko API error: {e}")
            return {}

    def get_coin_id(self, symbol: str) -> str:
        """Convert symbol to CoinGecko ID

        Args:
            symbol: Crypto symbol (e.g., "BTC", "ETH")

        Returns:
            CoinGecko ID (e.g., "bitcoin", "ethereum")
        """
        symbol = symbol.upper()

        # Check mapping first
        if symbol in self.SYMBOL_TO_ID:
            return self.SYMBOL_TO_ID[symbol]

        # If not in mapping, search via API
        data = self._make_request("/search", {"query": symbol})

        if data and "coins" in data and len(data["coins"]) > 0:
            # Return first match
            return data["coins"][0]["id"]

        # Fallback: lowercase symbol
        return symbol.lower()

    def get_price_history(
        self,
        symbol: str,
        days: int = 90,
        vs_currency: str = "usd"
    ) -> pd.DataFrame:
        """Get historical OHLC price data

        Args:
            symbol: Crypto symbol (e.g., "BTC")
            days: Number of days of history (max 365 for free tier)
            vs_currency: Quote currency (default: usd)

        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        coin_id = self.get_coin_id(symbol)

        # CoinGecko OHLC only accepts: 1, 7, 14, 30, 90, 180, 365 max
        # Round to nearest valid value
        valid_days = [1, 7, 14, 30, 90, 180, 365]
        days_param = min(valid_days, key=lambda x: abs(x - days))

        # CoinGecko OHLC endpoint (daily candles)
        data = self._make_request(
            f"/coins/{coin_id}/ohlc",
            params={
                "vs_currency": vs_currency,
                "days": days_param
            }
        )

        if not data:
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close"])

        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.set_index("timestamp")

        # Get volume data separately (market_chart endpoint)
        volume_data = self._make_request(
            f"/coins/{coin_id}/market_chart",
            params={
                "vs_currency": vs_currency,
                "days": min(days, 365)
            }
        )

        if volume_data and "total_volumes" in volume_data:
            volume_df = pd.DataFrame(volume_data["total_volumes"], columns=["timestamp", "volume"])
            volume_df["timestamp"] = pd.to_datetime(volume_df["timestamp"], unit="ms")
            volume_df = volume_df.set_index("timestamp")

            # Merge with OHLC data
            df = df.join(volume_df, how="left")
        else:
            df["volume"] = 0

        return df

    def get_current_price(
        self,
        symbol: str,
        vs_currency: str = "usd"
    ) -> Dict:
        """Get current price and basic market data

        Args:
            symbol: Crypto symbol
            vs_currency: Quote currency

        Returns:
            Dict with price, market_cap, volume, price_change_24h, etc.
        """
        coin_id = self.get_coin_id(symbol)

        data = self._make_request(
            f"/coins/{coin_id}",
            params={
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "false"
            }
        )

        if not data or "market_data" not in data:
            return {}

        market_data = data["market_data"]

        return {
            "symbol": symbol.upper(),
            "name": data.get("name", ""),
            "current_price": market_data.get("current_price", {}).get(vs_currency, 0),
            "market_cap": market_data.get("market_cap", {}).get(vs_currency, 0),
            "market_cap_rank": market_data.get("market_cap_rank", 0),
            "total_volume": market_data.get("total_volume", {}).get(vs_currency, 0),
            "price_change_24h": market_data.get("price_change_24h", 0),
            "price_change_percentage_24h": market_data.get("price_change_percentage_24h", 0),
            "price_change_percentage_7d": market_data.get("price_change_percentage_7d", 0),
            "price_change_percentage_30d": market_data.get("price_change_percentage_30d", 0),
            "circulating_supply": market_data.get("circulating_supply", 0),
            "total_supply": market_data.get("total_supply", 0),
            "max_supply": market_data.get("max_supply", 0),
            "ath": market_data.get("ath", {}).get(vs_currency, 0),
            "ath_change_percentage": market_data.get("ath_change_percentage", {}).get(vs_currency, 0),
            "ath_date": market_data.get("ath_date", {}).get(vs_currency, ""),
            "atl": market_data.get("atl", {}).get(vs_currency, 0),
            "atl_change_percentage": market_data.get("atl_change_percentage", {}).get(vs_currency, 0),
            "atl_date": market_data.get("atl_date", {}).get(vs_currency, ""),
        }

    def get_market_data_summary(
        self,
        symbol: str,
        days: int = 7
    ) -> str:
        """Get formatted market data summary for LLM

        Args:
            symbol: Crypto symbol
            days: Number of days for historical context

        Returns:
            Formatted string with market data
        """
        price_data = self.get_current_price(symbol)

        if not price_data:
            return f"Could not fetch market data for {symbol}"

        # Format max supply
        max_supply_str = f"{price_data['max_supply']:,.0f}" if price_data['max_supply'] else 'Unlimited'

        # Format dates
        ath_date_str = price_data['ath_date'][:10] if price_data['ath_date'] else 'N/A'
        atl_date_str = price_data['atl_date'][:10] if price_data['atl_date'] else 'N/A'

        summary = f"""
=== {price_data['name']} ({price_data['symbol']}) Market Data ===

Current Price: ${price_data['current_price']:,.2f}
Market Cap: ${price_data['market_cap']:,.0f} (Rank #{price_data['market_cap_rank']})
24h Volume: ${price_data['total_volume']:,.0f}

Price Changes:
  24h: {price_data['price_change_percentage_24h']:+.2f}%
  7d:  {price_data['price_change_percentage_7d']:+.2f}%
  30d: {price_data['price_change_percentage_30d']:+.2f}%

Supply:
  Circulating: {price_data['circulating_supply']:,.0f}
  Total: {price_data['total_supply']:,.0f}
  Max: {max_supply_str}

All-Time High: ${price_data['ath']:,.2f} ({price_data['ath_change_percentage']:+.2f}% from ATH)
  Date: {ath_date_str}

All-Time Low: ${price_data['atl']:,.2f} ({price_data['atl_change_percentage']:+.2f}% from ATL)
  Date: {atl_date_str}
"""

        return summary.strip()

    def get_trending_coins(self, limit: int = 10) -> List[Dict]:
        """Get trending cryptocurrencies

        Args:
            limit: Number of trending coins to return

        Returns:
            List of trending coins with basic data
        """
        data = self._make_request("/search/trending")

        if not data or "coins" not in data:
            return []

        trending = []
        for item in data["coins"][:limit]:
            coin = item.get("item", {})
            trending.append({
                "symbol": coin.get("symbol", ""),
                "name": coin.get("name", ""),
                "market_cap_rank": coin.get("market_cap_rank", 0),
                "price_btc": coin.get("price_btc", 0),
            })

        return trending

    def get_fear_greed_index(self) -> Dict:
        """Get crypto fear & greed index

        Note: This uses alternative.me API (separate from CoinGecko)

        Returns:
            Dict with value (0-100), classification, and timestamp
        """
        try:
            response = requests.get("https://api.alternative.me/fng/", timeout=10)
            response.raise_for_status()
            data = response.json()

            if data and "data" in data and len(data["data"]) > 0:
                latest = data["data"][0]
                return {
                    "value": int(latest.get("value", 50)),
                    "value_classification": latest.get("value_classification", "Neutral"),
                    "timestamp": latest.get("timestamp", ""),
                    "time_until_update": latest.get("time_until_update", "")
                }
        except Exception as e:
            print(f"Fear & Greed Index error: {e}")

        return {
            "value": 50,
            "value_classification": "Neutral",
            "timestamp": "",
            "time_until_update": ""
        }

    def get_global_market_data(self) -> Dict:
        """Get global crypto market statistics

        Returns:
            Dict with total market cap, volume, dominance, etc.
        """
        data = self._make_request("/global")

        if not data or "data" not in data:
            return {}

        global_data = data["data"]

        return {
            "active_cryptocurrencies": global_data.get("active_cryptocurrencies", 0),
            "markets": global_data.get("markets", 0),
            "total_market_cap_usd": global_data.get("total_market_cap", {}).get("usd", 0),
            "total_volume_usd": global_data.get("total_volume", {}).get("usd", 0),
            "market_cap_change_percentage_24h": global_data.get("market_cap_change_percentage_24h_usd", 0),
            "btc_dominance": global_data.get("market_cap_percentage", {}).get("btc", 0),
            "eth_dominance": global_data.get("market_cap_percentage", {}).get("eth", 0),
        }

    def get_global_market_summary(self) -> str:
        """Get formatted global market summary for LLM

        Returns:
            Formatted string with global market data
        """
        global_data = self.get_global_market_data()
        fear_greed = self.get_fear_greed_index()

        if not global_data:
            return "Could not fetch global market data"

        summary = f"""
=== Global Crypto Market Overview ===

Total Market Cap: ${global_data['total_market_cap_usd']:,.0f}
24h Market Cap Change: {global_data['market_cap_change_percentage_24h']:+.2f}%
Total 24h Volume: ${global_data['total_volume_usd']:,.0f}

Market Dominance:
  Bitcoin: {global_data['btc_dominance']:.2f}%
  Ethereum: {global_data['eth_dominance']:.2f}%

Active Cryptocurrencies: {global_data['active_cryptocurrencies']:,}
Active Markets: {global_data['markets']:,}

Fear & Greed Index: {fear_greed['value']}/100 ({fear_greed['value_classification']})
"""

        return summary.strip()


# Convenience functions for easy use
def get_crypto_price_history(symbol: str, days: int = 90) -> pd.DataFrame:
    """Convenience function to get price history"""
    utils = CoinGeckoUtils()
    return utils.get_price_history(symbol, days)


def get_crypto_current_price(symbol: str) -> Dict:
    """Convenience function to get current price"""
    utils = CoinGeckoUtils()
    return utils.get_current_price(symbol)


def get_crypto_market_summary(symbol: str) -> str:
    """Convenience function to get market summary"""
    utils = CoinGeckoUtils()
    return utils.get_market_data_summary(symbol)


# Example usage
if __name__ == "__main__":
    cg = CoinGeckoUtils()

    # Test BTC data
    print("Testing Bitcoin data...")
    print("\n" + "="*80)
    print(cg.get_market_data_summary("BTC"))

    print("\n" + "="*80)
    print(cg.get_global_market_summary())

    print("\n" + "="*80)
    print("Price History (last 5 days):")
    df = cg.get_price_history("BTC", days=5)
    print(df)

    print("\n" + "="*80)
    print("Trending Coins:")
    trending = cg.get_trending_coins(limit=5)
    for coin in trending:
        print(f"  {coin['symbol']}: {coin['name']} (Rank #{coin['market_cap_rank']})")
