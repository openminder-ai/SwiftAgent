import arxiv, asyncio

from swiftagent import SwiftAgent
from swiftagent.actions import action

agent = SwiftAgent()


# create action via decorator
@action(description="get information from arxiv about research papers")
def get_top_arxiv_articles(query: str) -> str:
    """
    Search arXiv and return content from top 3 articles matching the query.

    Args:
        query (str): Search query string

    Returns:
        str: Concatenated content from top 3 articles, including titles, authors,
             abstracts and links
    """
    # Create search client with custom parameters
    client = arxiv.Client()

    # Set up the search - sort by relevance, max 3 results
    search = arxiv.Search(
        query=query, max_results=3, sort_by=arxiv.SortCriterion.Relevance
    )

    # Initialize result string
    result = []

    # Fetch and process results
    for paper in client.results(search):
        # Format paper information
        paper_info = f"""
Title: {paper.title}
Authors: {', '.join(author.name for author in paper.authors)}
Published: {paper.published.strftime('%Y-%m-%d')}
Link: {paper.pdf_url}

Abstract:
{paper.summary}

----------------------------------------
"""
        result.append(paper_info)

    # Combine all results into single string
    return (
        "\n".join(result) if result else "No results found for the given query."
    )


# add action to agent
agent.add_action(get_top_arxiv_articles)


async def main():
    await agent.run(task="tell me about ProLLM")


if __name__ == "__main__":
    asyncio.run(main())
