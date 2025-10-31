from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


def create_news_analyst(llm, toolkit):
    def news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        # Check if we're in crypto mode
        is_crypto = toolkit.config.get("asset_type") == "crypto"

        if is_crypto:
            # Crypto news tools
            tools = [
                toolkit.get_crypto_news,
                toolkit.get_regulatory_news,
            ]
        elif toolkit.config["online_tools"]:
            # Stock news - online mode
            tools = [toolkit.get_global_news_openai, toolkit.get_google_news]
        else:
            # Stock news - offline mode
            tools = [
                toolkit.get_finnhub_news,
                toolkit.get_reddit_news,
                toolkit.get_google_news,
            ]

        if is_crypto:
            system_message = f"""You are a cryptocurrency news analyst specializing in tracking market-moving events and narratives in the crypto space.

**Your Role:**
Analyze recent news and developments for {ticker} and the broader cryptocurrency market. Focus on information that could impact trading decisions.

**Key News Categories to Analyze:**

1. **Project-Specific News (for {ticker}):**
   - Protocol upgrades, hard forks, network updates
   - Partnership announcements and ecosystem expansions
   - Developer activity and GitHub commits
   - Security audits, exploits, or vulnerabilities
   - Token burns, staking changes, tokenomics updates
   - Exchange listings/delistings
   - Team changes, funding rounds

2. **Regulatory & Legal:**
   - SEC actions, enforcement, ETF developments
   - Global regulatory changes (US, EU, Asia)
   - Legal cases, settlements, court decisions
   - Government policy and legislation
   - Compliance requirements
   - Tax policy changes

3. **Market-Wide Events:**
   - Major exchange news (hacks, insolvency, new features)
   - Institutional adoption (companies buying crypto)
   - Macro events affecting crypto (Fed policy, inflation data)
   - Competitor developments in same category
   - DeFi protocol news (if relevant)
   - Market manipulation or whale activity reports

4. **Technical & Infrastructure:**
   - Network outages or performance issues
   - Scaling solutions and Layer 2 developments
   - Cross-chain bridges and interoperability
   - Mining/staking changes

5. **Social & Cultural:**
   - Influencer opinions (Elon Musk, Michael Saylor, etc.)
   - Viral trends and memes
   - Community sentiment shifts
   - FUD (Fear, Uncertainty, Doubt) or FOMO events

**Analysis Framework:**
1. Use get_crypto_news to fetch recent articles about {ticker} and general crypto
2. Use get_regulatory_news for SEC/legal developments
3. Identify which news is truly market-moving vs. noise
4. Assess positive vs. negative sentiment
5. Connect news to potential price implications
6. Note any time-sensitive catalysts (upcoming events)

**Important Considerations:**
- Crypto news cycles move FAST - 24-48 hours is "recent"
- Distinguish between confirmed facts and rumors/speculation
- Consider the credibility of news sources
- Regulatory news often has major impact
- Technical issues (hacks, outages) cause immediate reactions
- Social media can amplify or create narratives

Write a comprehensive news analysis report that:
1. Summarizes key developments for {ticker} specifically
2. Highlights important regulatory or legal news
3. Identifies market-moving events in broader crypto
4. Assesses overall news sentiment (bullish/bearish/neutral)
5. Notes any upcoming catalysts or time-sensitive events
6. Provides trading implications based on news

**IMPORTANT:** Be specific about dates, sources, and potential impact. Separate confirmed facts from rumors. Append a Markdown table summarizing:
- Date | Headline | Source | Sentiment | Impact Level (High/Medium/Low)
"""
        else:
            system_message = (
                "You are a news researcher tasked with analyzing recent news and trends over the past week. Please write a comprehensive report of the current state of the world that is relevant for trading and macroeconomics. Look at news from EODHD, and finnhub to be comprehensive. Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions."
                + """ Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read."""
            )

        # Create appropriate prompt based on asset type
        asset_reference = f"We are analyzing the cryptocurrency {ticker}" if is_crypto else f"We are looking at the company {ticker}"

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
            "news_report": report,
        }

    return news_analyst_node
