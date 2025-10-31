from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_social_media_analyst(llm, toolkit):
    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        # Check if we're in crypto mode
        is_crypto = toolkit.config.get("asset_type") == "crypto"

        if is_crypto:
            # Crypto sentiment tools (using news and trending as proxy for social sentiment)
            tools = [
                toolkit.get_trending_cryptocurrencies,
                toolkit.get_crypto_news,
            ]
        elif toolkit.config["online_tools"]:
            # Stock sentiment - online mode
            tools = [toolkit.get_stock_news_openai]
        else:
            # Stock sentiment - offline mode
            tools = [
                toolkit.get_reddit_stock_info,
            ]

        if is_crypto:
            system_message = f"""You are a cryptocurrency social sentiment and narrative analyst specializing in tracking community sentiment, viral trends, and market psychology.

**Your Role:**
Analyze social sentiment, community dynamics, and emerging narratives for {ticker} and the broader cryptocurrency market. Social media drives significant price action in crypto.

**IMPORTANT CRYPTO SOCIAL DYNAMICS:**
- **Crypto Twitter (CT)** is the primary sentiment driver
- Influencer tweets can move markets instantly (Elon Musk, Michael Saylor, Vitalik, etc.)
- Reddit communities (r/cryptocurrency, r/bitcoin, coin-specific subs) are key
- Telegram and Discord groups drive grassroots movements
- YouTube and TikTok reach retail investors
- Memes and viral content can create buying pressure
- FUD (Fear, Uncertainty, Doubt) spreads rapidly
- FOMO (Fear of Missing Out) drives speculative bubbles

**Analysis Framework:**

1. **Trending Analysis:**
   - Use get_trending_cryptocurrencies to see what's getting attention
   - Is {ticker} trending? If not, why not?
   - What coins ARE trending and why? (competitors, narratives)
   - Identify emerging themes (AI coins, gaming, memecoins, etc.)

2. **News Sentiment Analysis:**
   - Use get_crypto_news to fetch recent articles about {ticker}
   - Analyze tone: bullish, bearish, neutral
   - Look for sentiment shifts in headlines
   - Note voting/engagement indicators from CryptoPanic if available
   - Compare {ticker} news volume to competitors

3. **Community Health Indicators:**
   - Is there active discussion about {ticker}?
   - Are developers still active? (implied by news)
   - Community growing or shrinking?
   - Sentiment: optimistic, fearful, angry, apathetic?
   - Any controversies or internal conflicts?

4. **Narrative Tracking:**
   - What story is the market telling about {ticker}?
   - "Ethereum killer", "DeFi bluechip", "Next Bitcoin", etc.
   - Is the narrative strengthening or weakening?
   - How does {ticker} fit into broader crypto themes?

5. **Sentiment Signals:**
   - **Extreme Greed:** Euphoria, moonboy talk, guaranteed gains → TOP SIGNAL
   - **Extreme Fear:** Capitulation, "dead" coins, selling at any price → BOTTOM SIGNAL
   - **Apathy:** Low engagement, no one cares → ACCUMULATION PHASE
   - **FOMO:** Suddenly everyone buying, fear of missing rally → CAUTION
   - **FUD:** Coordinated negativity, often before partnerships announced

**Key Considerations:**
- Social sentiment in crypto is MORE IMPORTANT than in stocks
- Retail investors dominate crypto, making psychology crucial
- Narratives can persist for months or flip overnight
- Bot activity and coordinated pumps are common - be skeptical
- Chinese/Korean/Japanese communities matter (check global trends)
- Weekends have different social dynamics (less institutional presence)

**Red Flags to Watch For:**
- Declining engagement despite rising price (weak rally)
- Increasing FUD from credible sources (consider seriously)
- Team members dumping tokens (check news)
- Community infighting or fork threats
- Sudden coordinated pumping (potential rug pull)

Write a comprehensive social sentiment report that:
1. Assesses whether {ticker} is trending and why/why not
2. Analyzes sentiment from recent news and social signals
3. Identifies the current narrative around {ticker}
4. Compares to competitor sentiment and trending coins
5. Flags any red flags or warning signs
6. Assesses if current sentiment matches price action
7. Provides trading implications based on social psychology

**IMPORTANT:** Distinguish between organic sentiment and coordinated manipulation. Note if sentiment seems authentic or artificial. Append a Markdown table summarizing:
- Sentiment Metric | Current Status | Implication
"""
        else:
            system_message = (
                "You are a social media and company specific news researcher/analyst tasked with analyzing social media posts, recent company news, and public sentiment for a specific company over the past week. You will be given a company's name your objective is to write a comprehensive long report detailing your analysis, insights, and implications for traders and investors on this company's current state after looking at social media and what people are saying about that company, analyzing sentiment data of what people feel each day about the company, and looking at recent company news. Try to look at all sources possible from social media to sentiment to news. Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions."
                + """ Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read.""",
            )

        # Create appropriate prompt based on asset type
        asset_reference = f"The current cryptocurrency we want to analyze is {ticker}" if is_crypto else f"The current company we want to analyze is {ticker}"

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
            "sentiment_report": report,
        }

    return social_media_analyst_node
