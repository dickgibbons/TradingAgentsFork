"""
Test Script for Crypto Trading Agents
Tests the complete crypto trading workflow with Bitcoin
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.crypto_config import CRYPTO_CONFIG, print_crypto_config_summary
from datetime import datetime

# Print configuration summary
print("\n" + "="*80)
print("CRYPTO TRADING AGENTS - TEST SCRIPT")
print("="*80 + "\n")

print_crypto_config_summary()

# Get today's date
today = datetime.now().strftime("%Y-%m-%d")
print(f"\n{'='*80}")
print(f"Testing with Bitcoin (BTC) on {today}")
print(f"{'='*80}\n")

# Create custom config for crypto
config = CRYPTO_CONFIG.copy()
config["llm_provider"] = "openai"  # Change as needed
config["deep_think_llm"] = "gpt-4o"  # Use powerful model for deep thinking
config["quick_think_llm"] = "gpt-4o-mini"  # Use fast model for quick analysis
config["max_debate_rounds"] = 2  # More rounds for crypto volatility
config["online_tools"] = False  # Use free crypto APIs

print("Initializing TradingAgentsGraph with crypto configuration...")
print(f"Selected Analysts: {config['selected_analysts']}")
print(f"- Market Analyst (crypto-aware)")
print(f"- On-Chain Analyst (blockchain metrics)")
print(f"- News Analyst (crypto news)")
print(f"- Social/Sentiment Analyst (trending & social)")
print()

# Initialize with crypto config and analysts
ta = TradingAgentsGraph(
    debug=True,
    config=config,
    selected_analysts=config['selected_analysts']  # ["market", "onchain", "news", "social"]
)

print(f"\nRunning analysis for BTC...\n")
print("="*80)

# Run the trading agents graph
try:
    _, decision = ta.propagate("BTC", today)

    print("\n" + "="*80)
    print("FINAL TRADING DECISION")
    print("="*80)
    print(decision)
    print("="*80 + "\n")

    print("✅ Crypto trading test completed successfully!")
    print("\nThe system has analyzed:")
    print("  - BTC price action and technical indicators")
    print("  - On-chain metrics (hash rate, mempool, whale activity)")
    print("  - Recent crypto news and regulatory developments")
    print("  - Social sentiment and trending coins")
    print("  - Global crypto market conditions (Fear & Greed Index)")
    print("\nAnd produced a comprehensive trading recommendation.")

except Exception as e:
    print(f"\n❌ Error during crypto trading test:")
    print(f"   {type(e).__name__}: {str(e)}")
    print("\nThis may be due to:")
    print("  - Missing API keys (check environment variables)")
    print("  - Network connectivity issues")
    print("  - Rate limiting on free APIs")
    print("  - Configuration errors")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
