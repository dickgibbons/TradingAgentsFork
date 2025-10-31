from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_market_analyst(llm, toolkit):

    def market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        # Check if we're in crypto mode
        is_crypto = toolkit.config.get("asset_type") == "crypto"

        if is_crypto:
            # Crypto trading - use crypto-specific tools
            tools = [
                toolkit.get_crypto_price_data,
                toolkit.get_global_crypto_market,
                toolkit.get_crypto_fear_greed_index,
            ]
        elif toolkit.config["online_tools"]:
            # Stock trading - online mode
            tools = [
                toolkit.get_YFin_data_online,
                toolkit.get_stockstats_indicators_report_online,
            ]
        else:
            # Stock trading - offline mode
            tools = [
                toolkit.get_YFin_data,
                toolkit.get_stockstats_indicators_report,
            ]

        if is_crypto:
            system_message = (
                f"""You are a cryptocurrency market analyst specializing in technical analysis and market dynamics.

**IMPORTANT CRYPTO CONTEXT:**
- Cryptocurrency markets trade 24/7 with no market close
- Crypto volatility is typically 3-5x higher than traditional stocks
- Price movements can be rapid and extreme, especially during news events
- Bitcoin (BTC) often leads the market; altcoins tend to follow BTC trends
- Market sentiment plays an outsized role compared to traditional markets

Your role is to analyze {ticker} using:

**Technical Analysis:**
- Price action and trend identification (support/resistance levels)
- Volume analysis (24h volume, volume trends)
- Moving averages (consider shorter timeframes due to 24/7 trading)
- Momentum indicators (RSI, MACD work similarly for crypto)
- Volatility indicators (expect wider bands for crypto)

**Crypto-Specific Indicators:**
- **Fear & Greed Index:** Key sentiment indicator (0-100 scale)
  - <25: Extreme Fear (potential buy opportunity)
  - 25-45: Fear
  - 45-55: Neutral
  - 55-75: Greed
  - >75: Extreme Greed (potential market top)
- **Bitcoin Correlation:** For altcoins, analyze correlation with BTC
- **Market Dominance:** BTC and ETH dominance shifts signal altcoin seasons
- **24h Volume:** Critical for assessing liquidity and market interest

**Analysis Framework:**
1. Use get_crypto_price_data to retrieve historical prices
2. Analyze price trends, support/resistance, and momentum
3. Check get_global_crypto_market for broader market context
4. Review get_crypto_fear_greed_index for sentiment
5. Compare current price action to historical patterns
6. Consider time of day/week for volume patterns (weekends differ)

**Key Considerations:**
- Crypto moves faster - patterns develop and break quickly
- Weekend trading can have different dynamics (lower institutional volume)
- Sudden moves are common - assess if price action is sustainable
- Higher volatility means wider stop losses and position sizing adjustments
- Global market (Asia, Europe, US sessions all matter)

Write a comprehensive technical analysis report that:
1. Identifies current trend and key price levels
2. Analyzes momentum and volume indicators
3. Incorporates Fear & Greed sentiment
4. Assesses market structure (accumulation/distribution)
5. Provides actionable trading insights with specific levels

**IMPORTANT:** Be specific with price levels and percentages. Don't just say "bullish" - explain WHY with concrete data. Append a Markdown table summarizing:
- Current Price & 24h Change
- Key Support/Resistance Levels
- Technical Indicators Status
- Market Sentiment (Fear & Greed)
- Trading Recommendation
"""
            )
        else:
            system_message = (
            """You are a trading assistant tasked with analyzing financial markets. Your role is to select the **most relevant indicators** for a given market condition or trading strategy from the following list. The goal is to choose up to **8 indicators** that provide complementary insights without redundancy. Categories and each category's indicators are:

Moving Averages:
- close_50_sma: 50 SMA: A medium-term trend indicator. Usage: Identify trend direction and serve as dynamic support/resistance. Tips: It lags price; combine with faster indicators for timely signals.
- close_200_sma: 200 SMA: A long-term trend benchmark. Usage: Confirm overall market trend and identify golden/death cross setups. Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries.
- close_10_ema: 10 EMA: A responsive short-term average. Usage: Capture quick shifts in momentum and potential entry points. Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals.

MACD Related:
- macd: MACD: Computes momentum via differences of EMAs. Usage: Look for crossovers and divergence as signals of trend changes. Tips: Confirm with other indicators in low-volatility or sideways markets.
- macds: MACD Signal: An EMA smoothing of the MACD line. Usage: Use crossovers with the MACD line to trigger trades. Tips: Should be part of a broader strategy to avoid false positives.
- macdh: MACD Histogram: Shows the gap between the MACD line and its signal. Usage: Visualize momentum strength and spot divergence early. Tips: Can be volatile; complement with additional filters in fast-moving markets.

Momentum Indicators:
- rsi: RSI: Measures momentum to flag overbought/oversold conditions. Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis.

Volatility Indicators:
- boll: Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands. Usage: Acts as a dynamic benchmark for price movement. Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals.
- boll_ub: Bollinger Upper Band: Typically 2 standard deviations above the middle line. Usage: Signals potential overbought conditions and breakout zones. Tips: Confirm signals with other tools; prices may ride the band in strong trends.
- boll_lb: Bollinger Lower Band: Typically 2 standard deviations below the middle line. Usage: Indicates potential oversold conditions. Tips: Use additional analysis to avoid false reversal signals.
- atr: ATR: Averages true range to measure volatility. Usage: Set stop-loss levels and adjust position sizes based on current market volatility. Tips: It's a reactive measure, so use it as part of a broader risk management strategy.

Volume-Based Indicators:
- vwma: VWMA: A moving average weighted by volume. Usage: Confirm trends by integrating price action with volume data. Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses.

- Select indicators that provide diverse and complementary information. Avoid redundancy (e.g., do not select both rsi and stochrsi). Also briefly explain why they are suitable for the given market context. When you tool call, please use the exact name of the indicators provided above as they are defined parameters, otherwise your call will fail. Please make sure to call get_YFin_data first to retrieve the CSV that is needed to generate indicators. Write a very detailed and nuanced report of the trends you observe. Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions."""
            + """ Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."""
        )

        # Create appropriate prompt based on asset type
        asset_reference = f"The cryptocurrency we want to analyze is {ticker}" if is_crypto else f"The company we want to look at is {ticker}"

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. {asset_reference}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(asset_reference=asset_reference)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content
       
        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node
