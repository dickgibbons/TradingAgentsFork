"""
Crypto-Specific Configuration for Trading Agents
Extends DEFAULT_CONFIG with cryptocurrency trading settings
"""

import os

try:
    from .default_config import DEFAULT_CONFIG
except ImportError:
    from default_config import DEFAULT_CONFIG


# Crypto-specific configuration
CRYPTO_CONFIG = DEFAULT_CONFIG.copy()

# Update config for crypto trading
CRYPTO_CONFIG.update({
    # ==================== ASSET TYPE ====================
    "asset_type": "crypto",  # "stock" or "crypto"

    # ==================== SUPPORTED CRYPTOCURRENCIES ====================
    "supported_tokens": [
        "BTC",    # Bitcoin
        "ETH",    # Ethereum
        "SOL",    # Solana
        "MATIC",  # Polygon
        "AVAX",   # Avalanche
        "BNB",    # Binance Coin
        "ADA",    # Cardano
        "DOT",    # Polkadot
        "LINK",   # Chainlink
        "UNI",    # Uniswap
    ],

    # Primary tokens to focus on (for testing/initial deployment)
    "primary_tokens": ["BTC", "ETH", "SOL"],

    # Base currency for trading pairs
    "base_currency": "USDT",  # Tether stablecoin

    # ==================== EXCHANGES ====================
    "exchanges": ["binance", "kraken", "coinbase"],
    "primary_exchange": "binance",

    # ==================== DATA SOURCES ====================
    "use_onchain_data": True,   # Enable blockchain metrics
    "use_defi_metrics": False,  # DeFi protocol data (future feature)
    "crypto_data_dir": "./crypto_data_cache",

    # ==================== TRADING HOURS ====================
    # Crypto markets are 24/7, but we can set preferred trading windows
    "trading_24_7": True,  # Crypto never closes
    "preferred_analysis_hours": None,  # Analyze anytime (vs stock market hours)

    # ==================== VOLATILITY ADJUSTMENTS ====================
    # Crypto is 3-5x more volatile than stocks
    "volatility_multiplier": 3.5,  # Adjust risk calculations
    "use_wider_stops": True,       # Wider stop losses for crypto volatility

    # ==================== ANALYST CONFIGURATION ====================
    # Which analysts to use (crypto-specific)
    "selected_analysts": [
        "market",       # Technical/Market Analyst (works for crypto)
        "onchain",      # On-Chain Analyst (replaces fundamentals)
        "news",         # News Analyst (crypto news sources)
        "social"        # Social/Sentiment Analyst (crypto Twitter)
    ],

    # ==================== API KEYS (from environment) ====================
    # Price & Market Data
    "coingecko_api_key": os.getenv("COINGECKO_API_KEY"),  # Optional (free tier works)

    # On-Chain Data
    "etherscan_api_key": os.getenv("ETHERSCAN_API_KEY"),  # For Ethereum on-chain
    "glassnode_api_key": os.getenv("GLASSNODE_API_KEY"),  # Premium on-chain (optional)
    "cryptocompare_api_key": os.getenv("CRYPTOCOMPARE_API_KEY"),  # Multi-chain data

    # News Sources
    "cryptopanic_api_key": os.getenv("CRYPTOPANIC_API_KEY"),  # Crypto news aggregator

    # Social Data
    "twitter_bearer_token": os.getenv("TWITTER_BEARER_TOKEN"),  # For crypto Twitter

    # ==================== CRYPTO-SPECIFIC INDICATORS ====================
    "use_fear_greed_index": True,        # Crypto Fear & Greed Index
    "monitor_whale_movements": True,     # Large wallet transactions
    "track_exchange_flows": True,        # Exchange inflows/outflows
    "monitor_funding_rates": False,      # Futures funding rates (future feature)

    # ==================== RISK MANAGEMENT ====================
    # Crypto-adjusted risk parameters
    "max_position_size": 0.15,  # Max 15% of portfolio in single crypto (vs 20% for stocks)
    "max_total_crypto_exposure": 0.80,  # Max 80% in crypto total
    "min_liquidity_24h": 10_000_000,  # Minimum $10M daily volume

    # ==================== DEBATE SETTINGS ====================
    # Keep same as DEFAULT_CONFIG, but can override
    "max_debate_rounds": 2,  # More rounds for volatile crypto markets
    "max_risk_discuss_rounds": 2,  # More risk discussion for crypto

    # ==================== MEMORY & LEARNING ====================
    "memory_enabled": True,
    "learn_from_crypto_cycles": True,  # Specific for crypto bull/bear cycles
    "track_halving_events": True,      # Bitcoin halving awareness
    "monitor_eth_upgrades": True,      # Ethereum network upgrades

    # ==================== ANALYSIS PREFERENCES ====================
    "prefer_onchain_over_fundamentals": True,  # On-chain > traditional fundamentals
    "weight_social_sentiment_higher": True,    # Social sentiment matters more in crypto
    "consider_network_effects": True,          # Network adoption is crucial

    # ==================== TIMEFRAMES ====================
    # Crypto moves faster than stocks
    "default_analysis_period_days": 30,  # vs 90 for stocks
    "news_lookback_hours": 48,           # vs 7 days for stocks
    "onchain_metrics_window": 7,         # Days of on-chain history
})


# Validation function
def validate_crypto_config(config: dict) -> tuple[bool, str]:
    """
    Validate crypto configuration

    Args:
        config: Configuration dictionary

    Returns:
        (is_valid, error_message) tuple
    """
    if config.get("asset_type") != "crypto":
        return False, "asset_type must be 'crypto'"

    if not config.get("supported_tokens"):
        return False, "supported_tokens list is empty"

    if not config.get("primary_tokens"):
        return False, "primary_tokens list is empty"

    # Check that primary tokens are in supported tokens
    for token in config.get("primary_tokens", []):
        if token not in config.get("supported_tokens", []):
            return False, f"Primary token {token} not in supported_tokens list"

    # Warn if no API keys set (but don't fail - can use free tier)
    warnings = []
    if not config.get("coingecko_api_key"):
        warnings.append("CoinGecko API key not set (using free tier)")

    if not config.get("etherscan_api_key"):
        warnings.append("Etherscan API key not set (Ethereum on-chain data limited)")

    if warnings:
        print("⚠️  Configuration Warnings:")
        for warning in warnings:
            print(f"   - {warning}")

    return True, "Configuration valid"


# Helper function to get crypto-specific analyst list
def get_crypto_analysts() -> list[str]:
    """Get list of analysts for crypto trading"""
    return CRYPTO_CONFIG["selected_analysts"]


# Helper function to check if running in crypto mode
def is_crypto_mode(config: dict = None) -> bool:
    """Check if system is configured for crypto trading"""
    cfg = config or CRYPTO_CONFIG
    return cfg.get("asset_type") == "crypto"


# Print configuration summary
def print_crypto_config_summary():
    """Print summary of crypto configuration"""
    print("="*80)
    print("CRYPTO TRADING CONFIGURATION")
    print("="*80)
    print(f"\nAsset Type: {CRYPTO_CONFIG['asset_type'].upper()}")
    print(f"\nPrimary Tokens: {', '.join(CRYPTO_CONFIG['primary_tokens'])}")
    print(f"Total Supported: {len(CRYPTO_CONFIG['supported_tokens'])} cryptocurrencies")
    print(f"\nExchanges: {', '.join(CRYPTO_CONFIG['exchanges'])}")
    print(f"Primary Exchange: {CRYPTO_CONFIG['primary_exchange']}")
    print(f"\nAnalysts:")
    for analyst in CRYPTO_CONFIG['selected_analysts']:
        print(f"  - {analyst.title()} Analyst")

    print(f"\nData Sources:")
    print(f"  On-Chain Data: {'✅ Enabled' if CRYPTO_CONFIG['use_onchain_data'] else '❌ Disabled'}")
    print(f"  Fear & Greed Index: {'✅ Enabled' if CRYPTO_CONFIG['use_fear_greed_index'] else '❌ Disabled'}")
    print(f"  Whale Monitoring: {'✅ Enabled' if CRYPTO_CONFIG['monitor_whale_movements'] else '❌ Disabled'}")

    print(f"\nRisk Management:")
    print(f"  Max Position Size: {CRYPTO_CONFIG['max_position_size']*100}%")
    print(f"  Max Total Exposure: {CRYPTO_CONFIG['max_total_crypto_exposure']*100}%")
    print(f"  Min 24h Liquidity: ${CRYPTO_CONFIG['min_liquidity_24h']:,}")

    print(f"\nMarket Characteristics:")
    print(f"  Trading: 24/7 (Always Open)")
    print(f"  Volatility Multiplier: {CRYPTO_CONFIG['volatility_multiplier']}x")

    print("\n" + "="*80)

    # Validate
    is_valid, message = validate_crypto_config(CRYPTO_CONFIG)
    if is_valid:
        print("✅ Configuration Valid")
    else:
        print(f"❌ Configuration Error: {message}")
    print("="*80)


# Export main config
__all__ = [
    "CRYPTO_CONFIG",
    "validate_crypto_config",
    "get_crypto_analysts",
    "is_crypto_mode",
    "print_crypto_config_summary",
]


# Auto-print on import (for debugging)
if __name__ == "__main__":
    print_crypto_config_summary()
