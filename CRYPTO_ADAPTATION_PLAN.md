# Crypto Trading Agents Adaptation Plan

## Overview
This document outlines the plan to adapt TradingAgentsFork from stock trading to crypto-only trading.

## Phase 1: Data Sources Replacement

### Current Stock Data Sources → Crypto Alternatives

| Stock Source | Purpose | Crypto Replacement | API |
|--------------|---------|-------------------|-----|
| YFinance | OHLCV price data | CoinGecko / Binance | Free/Paid |
| SimFin | Financial statements | On-chain metrics | Glassnode/Dune |
| Finnhub | Company news | Crypto news aggregator | CryptoPanic |
| StockStats | Technical indicators | TA-Lib (same) | Local library |
| Reddit | Social sentiment | Crypto Twitter/Reddit | Twitter API v2 |
| Google News | General news | Crypto news sites | Web scraping |

### New Crypto Data Sources to Add

1. **Price & Market Data**
   - CoinGecko API (free tier: 50 calls/min)
   - Binance API (high rate limits)
   - Kraken API (backup)

2. **On-Chain Metrics**
   - Glassnode (premium, comprehensive)
   - Alternative: Free blockchain explorers (Etherscan, etc.)
   - Messari API (free tier available)

3. **Social & Sentiment**
   - CryptoCompare Social Stats
   - LunarCrush (crypto social analytics)
   - Twitter/X API v2 (crypto influencers)
   - Reddit (r/cryptocurrency, r/bitcoin, etc.)

4. **News**
   - CryptoPanic API (news aggregator)
   - CoinTelegraph RSS
   - The Block API
   - Decrypt RSS feeds

5. **DeFi & Protocol Data**
   - DeFiLlama API (TVL, protocols)
   - Uniswap/DEX APIs (liquidity, volume)

## Phase 2: Agent Modifications

### Analysts Layer

#### 1. Technical/Market Analyst (MINOR CHANGES)
**Current**: Analyzes stock price charts with technical indicators
**Crypto**: Same indicators work (RSI, MACD, Bollinger Bands)
**Changes Needed**:
- Use crypto OHLCV data instead of stock data
- Add crypto-specific indicators:
  - Fear & Greed Index
  - Funding rates (futures markets)
  - Long/Short ratios
- Prompt update: Mention 24/7 trading, higher volatility

#### 2. On-Chain Analyst (NEW - REPLACES FUNDAMENTALS)
**Purpose**: Analyze blockchain metrics instead of financial statements
**Data Sources**:
- Holder distribution (whales, retail)
- Exchange inflows/outflows (selling pressure indicators)
- Active addresses (network usage)
- Transaction volume
- Supply metrics (circulating, locked, staked)
- Smart contract activity

**Prompt**:
```
You are an On-Chain Analyst specializing in blockchain metrics and on-chain data.

Your role is to:
1. Analyze holder distribution and whale wallet movements
2. Monitor exchange inflows/outflows to detect accumulation/distribution
3. Evaluate network activity (active addresses, transaction volume)
4. Assess tokenomics (supply, staking rates, unlock schedules)
5. Review smart contract interactions and DeFi protocol usage

Tools available:
- get_onchain_metrics(token, metric)
- get_whale_movements(token, days)
- get_exchange_flows(token, days)
- get_supply_metrics(token)
```

#### 3. News Analyst (MODERATE CHANGES)
**Current**: Analyzes macroeconomic news and company-specific news
**Crypto**: Analyze crypto-specific news and regulatory developments
**Changes Needed**:
- Replace Finnhub news with CryptoPanic/CoinTelegraph
- Focus on: regulations, protocol updates, security breaches, partnerships
- Consider global crypto sentiment (not just US)

**Prompt Updates**:
- Add: "Monitor regulatory developments in major markets"
- Add: "Track protocol upgrades, security audits, and exploits"
- Add: "Analyze macroeconomic factors (Fed policy, inflation, BTC halving cycles)"

#### 4. Social/Sentiment Analyst (MODERATE CHANGES)
**Current**: Reddit sentiment for stocks
**Crypto**: Twitter/X + Reddit + Telegram/Discord sentiment
**Changes Needed**:
- Replace stock subreddits with crypto subreddits
- Add Twitter/X monitoring (crypto influencers, project official accounts)
- Add social metrics: followers, engagement rate, sentiment scores
- Monitor Telegram/Discord activity (developer engagement)

**New Tools**:
- `get_twitter_crypto_sentiment(token, days)`
- `get_reddit_crypto_discussions(token, subreddit, days)`
- `get_social_metrics(token)` (followers, engagement)
- `get_github_activity(project)` (commits, contributors as development signal)

### Research Layer (MINOR CHANGES)

#### Bull Researcher
- Prompt update: Focus on crypto growth narratives (adoption, technology, DeFi)
- Memory: Learn from past crypto bull runs

#### Bear Researcher
- Prompt update: Focus on crypto risks (regulation, security, competition)
- Memory: Learn from past crypto crashes

#### Research Manager
- Prompt update: Understand crypto volatility and market cycles
- Memory: Pattern recognition for bull/bear markets

### Trading Layer (MINOR CHANGES)

#### Trader
- Prompt update: Account for 24/7 trading, no market close
- Add: Consider slippage and liquidity on different exchanges
- Add: Account for gas fees (for Ethereum-based tokens)

### Risk Management Layer (MODERATE CHANGES)

#### Risky, Safe, Neutral Analysts
- Prompt update: Crypto-specific risks
  - Smart contract risk
  - Regulatory risk (SEC classification)
  - Exchange risk (centralization)
  - Liquidity risk (low volume tokens)
  - Volatility risk (crypto is 3-5x more volatile than stocks)

#### Risk Manager
- Prompt update: Crypto portfolio management
  - Position sizing for high volatility
  - Correlation with BTC/ETH
  - Stablecoin exposure management

## Phase 3: Data Flow Architecture

### New Module Structure

```
tradingagents/dataflows/
├── interface.py              # Update to include crypto functions
├── crypto_utils.py           # NEW: Main crypto data wrapper
├── coingecko_utils.py        # NEW: CoinGecko API
├── binance_utils.py          # NEW: Binance API
├── onchain_utils.py          # NEW: Glassnode/on-chain metrics
├── cryptopanic_utils.py      # NEW: Crypto news
├── twitter_utils.py          # NEW: Twitter sentiment
├── defi_utils.py             # NEW: DeFi metrics
└── config.py                 # Update with crypto API keys
```

### interface.py Updates

Add new functions:
```python
@tool
def get_crypto_ohlcv(
    symbol: Annotated[str, "Crypto symbol (e.g., BTC, ETH)"],
    days: Annotated[int, "Number of days of historical data"] = 90
) -> str:
    """Get OHLCV price data for cryptocurrency"""

@tool
def get_onchain_metrics(
    symbol: Annotated[str, "Crypto symbol"],
    metric: Annotated[str, "Metric type: holders, flows, volume, supply"]
) -> str:
    """Get on-chain blockchain metrics"""

@tool
def get_crypto_news(
    symbol: Annotated[str, "Crypto symbol"],
    days: Annotated[int, "Days to look back"] = 7
) -> str:
    """Get crypto-specific news from multiple sources"""

@tool
def get_twitter_sentiment(
    symbol: Annotated[str, "Crypto symbol"],
    days: Annotated[int, "Days to analyze"] = 3
) -> str:
    """Get Twitter sentiment and social metrics"""

@tool
def get_defi_metrics(
    protocol: Annotated[str, "Protocol name or token"],
    metric: Annotated[str, "tvl, volume, users"]
) -> str:
    """Get DeFi protocol metrics"""
```

## Phase 4: Configuration Changes

### default_config.py Updates

```python
CRYPTO_CONFIG = {
    # Existing fields
    "project_dir": os.path.abspath(...),
    "results_dir": "./results",
    "llm_provider": "openai",
    "deep_think_llm": "o4-mini",
    "quick_think_llm": "gpt-4o-mini",

    # New crypto-specific fields
    "asset_type": "crypto",  # NEW
    "supported_tokens": ["BTC", "ETH", "SOL", "MATIC", "AVAX"],  # NEW
    "base_currency": "USDT",  # NEW
    "exchanges": ["binance", "kraken"],  # NEW

    # Data sources
    "use_onchain_data": True,  # NEW
    "use_defi_metrics": True,  # NEW
    "crypto_data_dir": "./crypto_data_cache",  # NEW

    # API keys (to be set via env vars)
    # COINGECKO_API_KEY, GLASSNODE_API_KEY, etc.

    # Existing debate settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "online_tools": True,
}
```

## Phase 5: Implementation Roadmap

### Step 1: Create Crypto Data Utilities (Week 1)
- [ ] Create `crypto_utils.py` with base CryptoDataFetcher class
- [ ] Implement `coingecko_utils.py` for price/market data
- [ ] Implement `binance_utils.py` for OHLCV and order book data
- [ ] Implement `onchain_utils.py` for blockchain metrics
- [ ] Implement `cryptopanic_utils.py` for news aggregation
- [ ] Create test suite for all data fetchers

### Step 2: Update Data Interface (Week 1-2)
- [ ] Add crypto tool functions to `interface.py`
- [ ] Update `agent_utils.py` to include crypto tools in toolkit
- [ ] Create crypto-specific tool nodes in `trading_graph.py`
- [ ] Test all tools individually

### Step 3: Create On-Chain Analyst (Week 2)
- [ ] Create `tradingagents/agents/analysts/onchain_analyst.py`
- [ ] Write comprehensive on-chain analysis prompt
- [ ] Test with sample crypto data

### Step 4: Update Existing Analysts (Week 2-3)
- [ ] Update market_analyst.py prompt for crypto
- [ ] Update news_analyst.py for crypto news sources
- [ ] Update social_media_analyst.py for Twitter + crypto Reddit
- [ ] Add crypto-specific technical indicators

### Step 5: Update Research & Trading Layers (Week 3)
- [ ] Update bull_researcher.py prompt with crypto narratives
- [ ] Update bear_researcher.py prompt with crypto risks
- [ ] Update research_manager.py for crypto decision making
- [ ] Update trader.py for 24/7 trading, exchange considerations

### Step 6: Update Risk Management (Week 3)
- [ ] Update risk analysts for crypto-specific risks
- [ ] Update risk_manager.py for crypto portfolio management
- [ ] Add volatility-adjusted position sizing

### Step 7: Update Graph & Configuration (Week 4)
- [ ] Add on-chain analyst node to graph workflow
- [ ] Update conditional edges for new analyst
- [ ] Create CRYPTO_CONFIG in default_config.py
- [ ] Update main.py with crypto example

### Step 8: Testing & Validation (Week 4-5)
- [ ] Test full pipeline with BTC
- [ ] Test with ETH, SOL, other major tokens
- [ ] Compare decisions with known market events
- [ ] Backtest on historical crypto data
- [ ] Create example outputs and documentation

### Step 9: CLI & Documentation (Week 5)
- [ ] Update CLI for crypto mode
- [ ] Create CRYPTO_README.md with usage examples
- [ ] Document API key requirements
- [ ] Create setup guide for crypto data sources

## Phase 6: API Keys & Setup Requirements

### Required API Keys

1. **CoinGecko** (Free tier sufficient for testing)
   - Sign up at https://www.coingecko.com/en/api
   - 50 calls/minute limit on free tier
   - `COINGECKO_API_KEY`

2. **Binance** (Free, high rate limits)
   - Create account at https://www.binance.com/
   - Generate API key (read-only for data fetching)
   - `BINANCE_API_KEY`, `BINANCE_SECRET_KEY`

3. **Glassnode** (OPTIONAL - premium on-chain data)
   - Expensive ($800+/month)
   - Alternative: Use free blockchain explorers
   - `GLASSNODE_API_KEY`

4. **CryptoPanic** (Free tier available)
   - News aggregation API
   - https://cryptopanic.com/developers/api/
   - `CRYPTOPANIC_API_KEY`

5. **Twitter/X API** (OPTIONAL - for social sentiment)
   - Free tier available with limitations
   - https://developer.twitter.com/
   - `TWITTER_BEARER_TOKEN`

6. **Keep Existing**:
   - `OPENAI_API_KEY` (for LLM calls)

### Free-Tier Implementation Strategy

For initial development without expensive APIs:
- Use CoinGecko free tier for price/market data
- Use public blockchain explorers (Etherscan API) for basic on-chain data
- Use Reddit API (free) for social sentiment
- Use RSS feeds for crypto news (no API key needed)
- Use public DeFiLlama API (free) for DeFi metrics

## Phase 7: Testing Plan

### Test Cases

1. **BTC Analysis** (2024-01-15)
   - Bull run scenario
   - Verify all analysts provide coherent reports
   - Check debate quality
   - Validate final decision

2. **ETH Analysis** (2024-03-20)
   - During network upgrade
   - Test on-chain analyst detection of events
   - Verify news analyst picks up upgrade info

3. **SOL Analysis** (2023-11-10)
   - During FTX collapse
   - Test risk management response
   - Verify news analyst flags major negative events

4. **Altcoin Analysis** (Various dates)
   - Test with lower liquidity tokens
   - Verify risk analysts flag liquidity concerns

## Success Metrics

- [ ] All data sources successfully integrated
- [ ] Agents produce coherent crypto-specific analysis
- [ ] Debate produces high-quality investment thesis
- [ ] Final decisions align with rational crypto analysis
- [ ] System handles major crypto events appropriately
- [ ] Performance on historical backtests > 55% win rate

## Migration Strategy

### Option 1: Fork Approach (RECOMMENDED)
- Create new branch: `crypto-only`
- Keep stock version on `main`
- Allows maintaining both versions

### Option 2: Configuration Toggle
- Add `asset_type` config parameter
- Use if/else logic to switch between stock and crypto
- More complex but maintains single codebase

**Recommendation**: Use Option 1 (Fork Approach) for cleaner separation

## Next Steps

1. Create `crypto-only` branch
2. Start with Phase 5, Step 1 (Crypto Data Utilities)
3. Incremental testing after each step
4. Regular commits with detailed messages

## Timeline Estimate

- **Week 1**: Data utilities and interface updates
- **Week 2**: Agent modifications (on-chain + updates)
- **Week 3**: Research, trading, risk layer updates
- **Week 4**: Graph integration and initial testing
- **Week 5**: Full testing, documentation, polish

**Total**: 5 weeks for full crypto adaptation

## Notes

- Start with major cryptocurrencies (BTC, ETH, SOL)
- Focus on free/low-cost data sources initially
- Can upgrade to premium data (Glassnode) later if needed
- 24/7 trading nature of crypto requires schedule adjustments
- Higher volatility requires risk management tuning
