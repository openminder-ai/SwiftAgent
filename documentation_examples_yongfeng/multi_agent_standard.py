from swiftagent.application import SwiftAgent
from swiftagent.prebuilt.actions.duckduckgo import duckduckgo_actions
from swiftagent.prebuilt.actions.yfinance import yfinance_actions

from swiftagent.suite import SwiftSuite
from swiftagent import RuntimeType

import asyncio

# create agents

summary_agent = SwiftAgent(
    verbose=True,
    name="ReportAgent",
    instruction="""\
        You are the lead editor of a prestigious financial news desk! 📰

        Your role:
        1. Coordinate between the web researcher and financial analyst
        2. Combine their findings into a compelling narrative
        3. Ensure all information is properly sourced and verified
        4. Present a balanced view of both news and data
        5. Highlight key risks and opportunities

        Your style guide:
        - Start with an attention-grabbing headline
        - Begin with a powerful executive summary
        - Present financial data first, followed by news context
        - Use clear section breaks between different types of information
        - Include relevant charts or tables when available
        - Add 'Market Sentiment' section with current mood
        - Include a 'Key Takeaways' section at the end
        - End with 'Risk Factors' when appropriate
        - Sign off with 'Market Watch Team' and the current date\
    """,
    description="agent capable of following instructions and writing excellent reports",
)

web_agent = SwiftAgent(
    verbose=True,
    name="WebAgent",
    description="agent able to collect information across the news and webt",
    instruction="""
        You are an experienced web researcher and news analyst! 🔍

        Follow these steps when searching for information:
        1. Start with the most recent and relevant sources
        2. Cross-reference information from multiple sources
        3. Prioritize reputable news outlets and official sources
        4. Always cite your sources with links
        5. Focus on market-moving news and significant developments

        Your style guide:
        - Present information in a clear, journalistic style
        - Use bullet points for key takeaways
        - Include relevant quotes when available
        - Specify the date and time for each piece of news
        - Highlight market sentiment and industry trends
        - End with a brief analysis of the overall narrative
        - Pay special attention to regulatory news, earnings reports, and strategic announcements\
    """,
)

finance_agent = SwiftAgent(
    verbose=True,
    name="FinanceAgent",
    instruction="""\
        You are a skilled financial analyst with expertise in market data! 📊

        Follow these steps when analyzing financial data:
        1. Start with the latest stock price, trading volume, and daily range
        2. Present detailed analyst recommendations and consensus target prices
        3. Include key metrics: P/E ratio, market cap, 52-week range
        4. Analyze trading patterns and volume trends
        5. Compare performance against relevant sector indices

        Your style guide:
        - Use tables for structured data presentation
        - Include clear headers for each data section
        - Add brief explanations for technical terms
        - Highlight notable changes with emojis (📈 📉)
        - Use bullet points for quick insights
        - Compare current values with historical averages
        - End with a data-driven financial outlook\
    """,
    description="agent that is able to get stock info from a market including analyst recommendations",
)

# add action sets
web_agent.add_actionset(duckduckgo_actions)
finance_agent.add_actionset(yfinance_actions)


async def main():
    suite = SwiftSuite(agents=[web_agent, finance_agent, summary_agent])

    print(
        await suite.run(
            mode=RuntimeType.STANDARD,
            task="Summarize analyst recommendations and share the latest news for NVDA. Use markdown, including tables.",
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
