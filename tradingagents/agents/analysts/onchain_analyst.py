"""
On-Chain Analyst for Cryptocurrency Trading
Analyzes blockchain metrics, network health, and whale movements
Replaces fundamentals analyst for crypto-specific trading
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_onchain_analyst(llm, toolkit):
    """
    Create on-chain analyst node for cryptocurrency analysis.

    This analyst replaces the fundamentals analyst when trading crypto.
    Instead of analyzing financial statements, it analyzes blockchain metrics:
    - Network health indicators (hash rate, difficulty, block times)
    - On-chain activity (transaction volume, whale movements)
    - Network congestion and fees
    - Exchange flows (inflows/outflows)
    - Staking and validator metrics

    Args:
        llm: Language model for analysis
        toolkit: Tool collection with crypto data access

    Returns:
        Node function for LangGraph workflow
    """
    def onchain_analyst_node(state):
        current_date = state["trade_date"]
        crypto_symbol = state["company_of_interest"]  # Actually crypto symbol (BTC, ETH, etc.)

        # Select appropriate on-chain tools based on crypto type
        # For Bitcoin: focus on hash rate, mempool, whale transactions
        # For Ethereum: focus on gas prices, staking, network activity
        # For others: general on-chain metrics

        if crypto_symbol.upper() == "BTC":
            tools = [
                toolkit.get_bitcoin_onchain_metrics,
                toolkit.get_crypto_price_data,
                toolkit.get_global_crypto_market,
            ]
        elif crypto_symbol.upper() == "ETH":
            tools = [
                toolkit.get_ethereum_onchain_metrics,
                toolkit.get_crypto_price_data,
                toolkit.get_global_crypto_market,
            ]
        else:
            tools = [
                toolkit.get_onchain_metrics,
                toolkit.get_crypto_price_data,
                toolkit.get_global_crypto_market,
            ]

        system_message = f"""You are an on-chain analyst specializing in cryptocurrency blockchain analysis. Your role is to analyze on-chain metrics and network health indicators to provide insights for crypto trading decisions.

For {crypto_symbol}, you should analyze:

**Network Health Indicators:**
- Hash rate / mining power (security indicator)
- Network difficulty and block times
- Miner revenue and incentives
- Validator participation (for PoS chains)

**On-Chain Activity:**
- Transaction volume and count (24h and trends)
- Large transactions (whale movements >50 BTC or equivalent)
- Exchange inflows/outflows (selling vs. accumulation signals)
- Active addresses and network usage

**Network Economics:**
- Fee levels (mempool congestion for BTC, gas prices for ETH)
- Transaction costs and their impact on usage
- Network congestion level
- Block space demand

**Market Structure:**
- Supply dynamics (circulating vs. total supply)
- Distribution of holdings (whale concentration)
- Exchange reserves (available selling pressure)
- Staking metrics (supply locked, validator count)

**Context and Interpretation:**
- Compare current metrics to historical norms
- Identify unusual patterns or anomalies
- Assess whether on-chain data confirms or contradicts price action
- Consider network effects and adoption trends
- Evaluate security and decentralization health

Write a comprehensive on-chain analysis report that:
1. Summarizes current network health and activity levels
2. Highlights any significant whale movements or exchange flows
3. Assesses whether on-chain metrics suggest accumulation or distribution
4. Identifies potential risks (congestion, security concerns, centralization)
5. Provides actionable insights for trading decisions

Make sure to be specific and data-driven. Don't just say "metrics look healthy" - provide actual numbers and context. Compare to historical levels when relevant.

**IMPORTANT:** Append a Markdown table at the end summarizing key on-chain metrics with current values, historical context, and trading implications.

Current date: {current_date}
Cryptocurrency: {crypto_symbol}
"""

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
                    "For your reference, the current date is {current_date}. The cryptocurrency we want to analyze is {crypto_symbol}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(crypto_symbol=crypto_symbol)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        # If no tool calls, the LLM has generated the final report
        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "onchain_report": report,  # New state field for on-chain analysis
        }

    return onchain_analyst_node
