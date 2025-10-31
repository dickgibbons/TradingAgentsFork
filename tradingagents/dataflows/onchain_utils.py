"""
On-Chain Metrics Utilities for Crypto Trading Agents
Provides blockchain data analysis using free-tier APIs
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import time
import os


class OnChainUtils:
    """Wrapper for on-chain blockchain metrics using multiple free APIs"""

    def __init__(
        self,
        cryptocompare_api_key: Optional[str] = None,
        etherscan_api_key: Optional[str] = None,
        glassnode_api_key: Optional[str] = None
    ):
        """Initialize on-chain data client

        Args:
            cryptocompare_api_key: CryptoCompare API key (free tier available)
            etherscan_api_key: Etherscan API key (free tier: 5 calls/sec)
            glassnode_api_key: Glassnode API key (premium, optional)
        """
        self.cryptocompare_key = cryptocompare_api_key or os.getenv("CRYPTOCOMPARE_API_KEY")
        self.etherscan_key = etherscan_api_key or os.getenv("ETHERSCAN_API_KEY")
        self.glassnode_key = glassnode_api_key or os.getenv("GLASSNODE_API_KEY")

        self.last_request_time = {}
        self.rate_limit_delay = 1.0  # Default 1 second between requests

    def _rate_limit(self, api_name: str):
        """Enforce rate limiting per API"""
        current_time = time.time()
        last_time = self.last_request_time.get(api_name, 0)
        time_since_last = current_time - last_time

        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)

        self.last_request_time[api_name] = time.time()

    def _make_request(self, url: str, params: Dict = None, api_name: str = "default") -> Dict:
        """Make API request with error handling

        Args:
            url: Full URL to request
            params: Query parameters
            api_name: Name for rate limiting

        Returns:
            JSON response as dict
        """
        self._rate_limit(api_name)

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"On-chain API error ({api_name}): {e}")
            return {}

    # ==================== BITCOIN ON-CHAIN METRICS ====================

    def get_bitcoin_network_stats(self) -> Dict:
        """Get Bitcoin network statistics from Blockchain.com API (free)

        Returns:
            Dict with hash rate, difficulty, transaction count, etc.
        """
        url = "https://blockchain.info/stats?format=json"
        data = self._make_request(url, api_name="blockchain.com")

        if not data:
            return {}

        return {
            "market_price_usd": data.get("market_price_usd", 0),
            "hash_rate": data.get("hash_rate", 0),  # GH/s
            "difficulty": data.get("difficulty", 0),
            "total_btc_sent": data.get("total_btc_sent", 0) / 1e8,  # Convert to BTC
            "n_transactions": data.get("n_tx", 0),
            "n_blocks_total": data.get("n_blocks_total", 0),
            "minutes_between_blocks": data.get("minutes_between_blocks", 0),
            "totalbc": data.get("totalbc", 0) / 1e8,  # Total BTC mined
            "estimated_transaction_volume_usd": data.get("estimated_transaction_volume_usd", 0),
            "blocks_size": data.get("blocks_size", 0),
            "miners_revenue_usd": data.get("miners_revenue_usd", 0),
            "timestamp": data.get("timestamp", 0),
        }

    def get_bitcoin_mempool_info(self) -> Dict:
        """Get Bitcoin mempool statistics (pending transactions)

        Returns:
            Dict with mempool size, fees, etc.
        """
        url = "https://blockchain.info/q/unconfirmedcount"

        try:
            response = requests.get(url, timeout=10)
            unconfirmed_count = int(response.text)

            return {
                "unconfirmed_transactions": unconfirmed_count,
                "mempool_size_mb": unconfirmed_count * 0.0005,  # Rough estimate
                "congestion_level": "High" if unconfirmed_count > 10000 else "Low" if unconfirmed_count < 2000 else "Medium"
            }
        except Exception as e:
            print(f"Mempool API error: {e}")
            return {}

    def get_bitcoin_large_transactions(self, min_value_btc: float = 100) -> List[Dict]:
        """Get recent large Bitcoin transactions (whale watching)

        Args:
            min_value_btc: Minimum transaction value in BTC

        Returns:
            List of large transactions
        """
        url = "https://blockchain.info/unconfirmed-transactions?format=json"
        data = self._make_request(url, api_name="blockchain.com")

        if not data or "txs" not in data:
            return []

        large_txs = []
        for tx in data.get("txs", [])[:20]:  # Check first 20 transactions
            value_btc = tx.get("out", [{}])[0].get("value", 0) / 1e8 if tx.get("out") else 0

            if value_btc >= min_value_btc:
                large_txs.append({
                    "hash": tx.get("hash", ""),
                    "value_btc": value_btc,
                    "value_usd": value_btc * self.get_bitcoin_network_stats().get("market_price_usd", 0),
                    "time": datetime.fromtimestamp(tx.get("time", 0)),
                    "size": tx.get("size", 0),
                })

        return large_txs

    # ==================== ETHEREUM ON-CHAIN METRICS ====================

    def get_ethereum_gas_stats(self) -> Dict:
        """Get Ethereum gas prices and network activity

        Returns:
            Dict with gas prices, gas limit, etc.
        """
        if not self.etherscan_key:
            return {"error": "Etherscan API key required"}

        url = "https://api.etherscan.io/api"
        params = {
            "module": "gastracker",
            "action": "gasoracle",
            "apikey": self.etherscan_key
        }

        data = self._make_request(url, params, api_name="etherscan")

        if not data or data.get("status") != "1":
            return {}

        result = data.get("result", {})

        return {
            "safe_gas_price": int(result.get("SafeGasPrice", 0)),  # Gwei
            "propose_gas_price": int(result.get("ProposeGasPrice", 0)),
            "fast_gas_price": int(result.get("FastGasPrice", 0)),
            "suggested_base_fee": float(result.get("suggestBaseFee", 0)),
            "gas_used_ratio": result.get("gasUsedRatio", ""),
            "network_congestion": "High" if int(result.get("FastGasPrice", 0)) > 50 else "Low" if int(result.get("FastGasPrice", 0)) < 20 else "Medium"
        }

    def get_ethereum_supply_stats(self) -> Dict:
        """Get Ethereum supply statistics

        Returns:
            Dict with total supply, burned ETH, etc.
        """
        if not self.etherscan_key:
            return {"error": "Etherscan API key required"}

        url = "https://api.etherscan.io/api"

        # Get total supply
        params = {
            "module": "stats",
            "action": "ethsupply",
            "apikey": self.etherscan_key
        }

        data = self._make_request(url, params, api_name="etherscan")

        if not data or data.get("status") != "1":
            return {}

        total_supply = int(data.get("result", 0)) / 1e18  # Convert Wei to ETH

        # Get ETH2 staking stats
        params["action"] = "ethsupply2"
        data2 = self._make_request(url, params, api_name="etherscan")

        return {
            "total_supply_eth": total_supply,
            "eth2_staking": data2.get("result", {}) if data2.get("status") == "1" else {},
        }

    # ==================== MULTI-CHAIN METRICS (CryptoCompare) ====================

    def get_on_chain_summary(self, symbol: str) -> Dict:
        """Get on-chain summary from CryptoCompare

        Args:
            symbol: Crypto symbol (BTC, ETH, etc.)

        Returns:
            Dict with various on-chain metrics
        """
        if not self.cryptocompare_key:
            return {"error": "CryptoCompare API key required"}

        url = "https://min-api.cryptocompare.com/data/blockchain/latest"
        headers = {"authorization": f"Apikey {self.cryptocompare_key}"}
        params = {"fsym": symbol.upper()}

        self._rate_limit("cryptocompare")

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("Response") == "Success" and "Data" in data:
                return data["Data"]
            else:
                return {}
        except Exception as e:
            print(f"CryptoCompare on-chain error: {e}")
            return {}

    def get_social_stats(self, symbol: str) -> Dict:
        """Get social media statistics from CryptoCompare

        Args:
            symbol: Crypto symbol

        Returns:
            Dict with Reddit, Twitter, GitHub stats
        """
        if not self.cryptocompare_key:
            return {"error": "CryptoCompare API key required"}

        url = "https://min-api.cryptocompare.com/data/social/coin/latest"
        headers = {"authorization": f"Apikey {self.cryptocompare_key}"}
        params = {"coinId": self._get_cryptocompare_coin_id(symbol)}

        self._rate_limit("cryptocompare")

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("Response") == "Success" and "Data" in data:
                social_data = data["Data"]

                return {
                    "reddit_subscribers": social_data.get("Reddit", {}).get("subscribers", 0),
                    "reddit_active_users": social_data.get("Reddit", {}).get("active_users", 0),
                    "reddit_posts_per_day": social_data.get("Reddit", {}).get("posts_per_day", 0),
                    "twitter_followers": social_data.get("Twitter", {}).get("followers", 0),
                    "twitter_statuses": social_data.get("Twitter", {}).get("statuses", 0),
                }
            else:
                return {}
        except Exception as e:
            print(f"CryptoCompare social error: {e}")
            return {}

    def _get_cryptocompare_coin_id(self, symbol: str) -> int:
        """Get CryptoCompare coin ID from symbol

        Args:
            symbol: Crypto symbol

        Returns:
            CryptoCompare internal coin ID
        """
        # Common mappings
        mappings = {
            "BTC": 1182,
            "ETH": 7605,
            "SOL": 699785,
            "MATIC": 321992,
            "AVAX": 893373,
        }

        return mappings.get(symbol.upper(), 0)

    # ==================== GLASSNODE METRICS (Premium) ====================

    def get_glassnode_metric(
        self,
        symbol: str,
        metric: str,
        interval: str = "24h"
    ) -> pd.DataFrame:
        """Get metric from Glassnode API (requires premium subscription)

        Args:
            symbol: Crypto symbol (BTC, ETH)
            metric: Metric name (e.g., "addresses/active_count")
            interval: Time interval (1h, 24h, 1w, 1month)

        Returns:
            DataFrame with timestamp and value columns
        """
        if not self.glassnode_key:
            return pd.DataFrame()

        url = f"https://api.glassnode.com/v1/metrics/{metric}"
        params = {
            "a": symbol.upper(),
            "i": interval,
            "api_key": self.glassnode_key
        }

        self._rate_limit("glassnode")

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data:
                df = pd.DataFrame(data)
                df["timestamp"] = pd.to_datetime(df["t"], unit="s")
                df = df.rename(columns={"v": "value"})
                return df[["timestamp", "value"]].set_index("timestamp")
            else:
                return pd.DataFrame()
        except Exception as e:
            print(f"Glassnode API error: {e}")
            return pd.DataFrame()

    # ==================== FORMATTED SUMMARIES FOR LLM ====================

    def get_bitcoin_onchain_summary(self) -> str:
        """Get formatted Bitcoin on-chain summary for LLM

        Returns:
            Formatted string with Bitcoin on-chain metrics
        """
        network_stats = self.get_bitcoin_network_stats()
        mempool_info = self.get_bitcoin_mempool_info()
        large_txs = self.get_bitcoin_large_transactions(min_value_btc=50)

        if not network_stats:
            return "Could not fetch Bitcoin on-chain data"

        summary = f"""
=== Bitcoin On-Chain Metrics ===

Network Health:
  Hash Rate: {network_stats['hash_rate'] / 1e9:.2f} EH/s
  Difficulty: {network_stats['difficulty']:,.0f}
  Avg Block Time: {network_stats['minutes_between_blocks']:.1f} minutes
  Total BTC Mined: {network_stats['totalbc']:,.2f} BTC

Transaction Activity (24h):
  Total Transactions: {network_stats['n_transactions']:,}
  Volume: ${network_stats['estimated_transaction_volume_usd']:,.0f}
  Miner Revenue: ${network_stats['miners_revenue_usd']:,.0f}

Mempool Status:
  Unconfirmed Transactions: {mempool_info.get('unconfirmed_transactions', 'N/A'):,}
  Network Congestion: {mempool_info.get('congestion_level', 'Unknown')}

Whale Activity (Recent Large Transactions):
"""

        if large_txs:
            for i, tx in enumerate(large_txs[:5], 1):
                summary += f"\n  {i}. {tx['value_btc']:.2f} BTC (${tx['value_usd']:,.0f})"
        else:
            summary += "\n  No large transactions detected recently"

        return summary.strip()

    def get_ethereum_onchain_summary(self) -> str:
        """Get formatted Ethereum on-chain summary for LLM

        Returns:
            Formatted string with Ethereum on-chain metrics
        """
        gas_stats = self.get_ethereum_gas_stats()
        supply_stats = self.get_ethereum_supply_stats()

        if "error" in gas_stats:
            return "Etherscan API key required for Ethereum on-chain data"

        summary = f"""
=== Ethereum On-Chain Metrics ===

Network Activity:
  Gas Prices (Gwei):
    Safe: {gas_stats['safe_gas_price']}
    Standard: {gas_stats['propose_gas_price']}
    Fast: {gas_stats['fast_gas_price']}
  Base Fee: {gas_stats['suggested_base_fee']:.2f} Gwei
  Network Congestion: {gas_stats['network_congestion']}

Supply Metrics:
  Total Supply: {supply_stats.get('total_supply_eth', 0):,.0f} ETH
"""

        return summary.strip()

    def get_general_onchain_summary(self, symbol: str) -> str:
        """Get formatted on-chain summary for any crypto

        Args:
            symbol: Crypto symbol

        Returns:
            Formatted string with on-chain metrics
        """
        if symbol.upper() == "BTC":
            return self.get_bitcoin_onchain_summary()
        elif symbol.upper() == "ETH":
            return self.get_ethereum_onchain_summary()
        else:
            # Generic summary using CryptoCompare
            onchain_data = self.get_on_chain_summary(symbol)
            social_data = self.get_social_stats(symbol)

            if not onchain_data and not social_data:
                return f"Limited on-chain data available for {symbol}"

            summary = f"=== {symbol.upper()} On-Chain & Social Metrics ===\n"

            if social_data:
                summary += f"""
Social Activity:
  Reddit Subscribers: {social_data.get('reddit_subscribers', 0):,}
  Reddit Active Users: {social_data.get('reddit_active_users', 0):,}
  Twitter Followers: {social_data.get('twitter_followers', 0):,}
"""

            return summary.strip()


# Convenience functions for easy use
def get_bitcoin_metrics() -> str:
    """Convenience function to get Bitcoin on-chain summary"""
    utils = OnChainUtils()
    return utils.get_bitcoin_onchain_summary()


def get_ethereum_metrics() -> str:
    """Convenience function to get Ethereum on-chain summary"""
    utils = OnChainUtils()
    return utils.get_ethereum_onchain_summary()


def get_onchain_metrics(symbol: str) -> str:
    """Convenience function to get on-chain summary for any crypto"""
    utils = OnChainUtils()
    return utils.get_general_onchain_summary(symbol)


# Example usage
if __name__ == "__main__":
    onchain = OnChainUtils()

    print("="*80)
    print("BITCOIN ON-CHAIN ANALYSIS")
    print("="*80)
    print(onchain.get_bitcoin_onchain_summary())

    print("\n" + "="*80)
    print("ETHEREUM ON-CHAIN ANALYSIS")
    print("="*80)
    print(onchain.get_ethereum_onchain_summary())

    print("\n" + "="*80)
    print("BITCOIN NETWORK STATS (Detailed)")
    print("="*80)
    stats = onchain.get_bitcoin_network_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
