import json
from os import getenv
from typing import Any, Dict, List, Optional

from swiftagent.actions.set import ActionSet

try:
    from exa_py import Exa
except ImportError:
    raise ImportError(
        "`exa_py` not installed. Please install using `pip install exa_py`"
    )


exa_actions = ActionSet(
    name="exa",
    description=(
        "Exa toolkit actions for performing searches, retrieving content, "
        "finding similar results, and getting LLM-informed answers via the Exa API."
    ),
)


def _parse_results(
    exa_results: Any, text_length_limit: int, highlights: bool
) -> str:
    """
    Parse the Exa search results into a JSON string.

    Args:
        exa_results: The raw response from Exa.
        text_length_limit: Maximum number of characters to include from each result's text.
        highlights: Whether to include highlighted snippets.

    Returns:
        A JSON-formatted string of parsed results.
    """
    exa_results_parsed = []
    for result in exa_results.results:
        result_dict = {"url": result.url}
        if getattr(result, "title", None):
            result_dict["title"] = result.title
        if getattr(result, "author", None) and result.author != "":
            result_dict["author"] = result.author
        if getattr(result, "published_date", None):
            result_dict["published_date"] = result.published_date
        if getattr(result, "text", None):
            _text = result.text
            if text_length_limit:
                _text = _text[:text_length_limit]
            result_dict["text"] = _text
        if highlights:
            try:
                if getattr(result, "highlights", None):
                    result_dict["highlights"] = result.highlights
            except Exception as e:
                result_dict["highlights"] = f"Failed to get highlights: {e}"
        exa_results_parsed.append(result_dict)
    return json.dumps(exa_results_parsed, indent=4)


@exa_actions.action(
    params={
        "query": "The query to search for.",
        "num_results": "Number of results to return (default: 5).",
        "category": (
            "Optional category to filter search results (e.g., 'news', 'research paper', etc.)."
        ),
        "api_key": "Exa API key. If not provided, will use the EXA_API_KEY environment variable.",
        "text": "Retrieve text content from results (default: True).",
        "text_length_limit": "Max length of text content per result (default: 1000).",
        "highlights": "Include highlighted snippets (default: True).",
        "summary": "Include summary in results (default: False).",
        "livecrawl": "Crawl mode (default: 'always').",
        "start_crawl_date": "Include results crawled on/after this date (YYYY-MM-DD).",
        "end_crawl_date": "Include results crawled on/before this date (YYYY-MM-DD).",
        "start_published_date": "Include results published on/after this date (YYYY-MM-DD).",
        "end_published_date": "Include results published on/before this date (YYYY-MM-DD).",
        "use_autoprompt": "Enable autoprompt features in queries.",
        "type": "Specify content type (e.g., 'article', 'blog', 'video').",
        "include_domains": "List of domains to restrict results to.",
        "exclude_domains": "List of domains to exclude from results.",
        "show_results": "Log search results for debugging (default: False).",
    },
    strict=False,
    name="exa_search",
)
def exa_search(
    query: str,
    num_results: int = 5,
    category: Optional[str] = None,
    text: bool = True,
    text_length_limit: int = 1000,
    highlights: bool = True,
    summary: bool = False,
    livecrawl: str = "always",
    start_crawl_date: Optional[str] = None,
    end_crawl_date: Optional[str] = None,
    start_published_date: Optional[str] = None,
    end_published_date: Optional[str] = None,
    use_autoprompt: Optional[bool] = None,
    type: Optional[str] = None,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
) -> str:
    """
    Search Exa for a query.

    Returns:
        str: Search results in JSON format.
    """
    api_key = getenv("EXA_API_KEY")
    if not api_key:
        return "Error: EXA_API_KEY not set."
    exa = Exa(api_key)
    search_kwargs: Dict[str, Any] = {
        "text": text,
        "highlights": highlights,
        "summary": summary,
        "num_results": num_results,
        "livecrawl": livecrawl,
        "start_crawl_date": start_crawl_date,
        "end_crawl_date": end_crawl_date,
        "start_published_date": start_published_date,
        "end_published_date": end_published_date,
        "use_autoprompt": use_autoprompt,
        "type": type,
        "category": category,
        "include_domains": include_domains,
        "exclude_domains": exclude_domains,
    }
    # Remove keys with None values
    search_kwargs = {k: v for k, v in search_kwargs.items() if v is not None}
    try:
        exa_results = exa.search_and_contents(query, **search_kwargs)
        parsed_results = _parse_results(
            exa_results, text_length_limit, highlights
        )

        return parsed_results
    except Exception as e:
        return f"Error: {e}"


@exa_actions.action(
    params={
        "urls": "List of URLs to retrieve content from.",
        "text": "Retrieve text content (default: True).",
        "text_length_limit": "Max length of text content per result (default: 1000).",
        "highlights": "Include highlighted snippets (default: True).",
        "summary": "Include summary in results (default: False).",
    },
    strict=False,
    name="exa_get_contents",
)
def exa_get_contents(
    urls: List[str],
    text: bool = True,
    text_length_limit: int = 1000,
    highlights: bool = True,
    summary: bool = False,
) -> str:
    """
    Retrieve detailed content from specific URLs using the Exa API.

    Returns:
        str: The retrieved contents in JSON format.
    """
    api_key = getenv("EXA_API_KEY")
    if not api_key:
        return "Error: EXA_API_KEY not set."
    exa = Exa(api_key)
    query_kwargs = {
        "text": text,
        "highlights": highlights,
        "summary": summary,
    }
    try:
        exa_results = exa.get_contents(urls=urls, **query_kwargs)
        parsed_results = _parse_results(
            exa_results, text_length_limit, highlights
        )

        return parsed_results
    except Exception as e:
        return f"Error: {e}"


@exa_actions.action(
    params={
        "url": "The URL to find similar content for.",
        "num_results": "Number of similar results to return (default: 5).",
        "text": "Retrieve text content (default: True).",
        "text_length_limit": "Max length of text per result (default: 1000).",
        "highlights": "Include highlighted snippets (default: True).",
        "summary": "Include summary in results (default: False).",
        "include_domains": "List of domains to restrict results.",
        "exclude_domains": "List of domains to exclude.",
        "start_crawl_date": "Include results crawled on/after this date (YYYY-MM-DD).",
        "end_crawl_date": "Include results crawled on/before this date (YYYY-MM-DD).",
        "start_published_date": "Include results published on/after this date (YYYY-MM-DD).",
        "end_published_date": "Include results published on/before this date (YYYY-MM-DD).",
    },
    strict=False,
    name="exa_find_similar",
)
def exa_find_similar(
    url: str,
    num_results: int = 5,
    text: bool = True,
    text_length_limit: int = 1000,
    highlights: bool = True,
    summary: bool = False,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    start_crawl_date: Optional[str] = None,
    end_crawl_date: Optional[str] = None,
    start_published_date: Optional[str] = None,
    end_published_date: Optional[str] = None,
) -> str:
    """
    Find similar links to a given URL using the Exa API.

    Returns:
        str: Similar results in JSON format.
    """
    api_key = getenv("EXA_API_KEY")
    if not api_key:
        return "Error: EXA_API_KEY not set."
    exa = Exa(api_key)
    query_kwargs = {
        "text": text,
        "highlights": highlights,
        "summary": summary,
        "include_domains": include_domains,
        "exclude_domains": exclude_domains,
        "start_crawl_date": start_crawl_date,
        "end_crawl_date": end_crawl_date,
        "start_published_date": start_published_date,
        "end_published_date": end_published_date,
        "num_results": num_results,
    }
    query_kwargs = {k: v for k, v in query_kwargs.items() if v is not None}
    try:
        exa_results = exa.find_similar_and_contents(url=url, **query_kwargs)
        parsed_results = _parse_results(
            exa_results, text_length_limit, highlights
        )

        return parsed_results
    except Exception as e:
        return f"Error: {e}"


@exa_actions.action(
    params={
        "query": "The question or query to get an answer for.",
        "text": "Include full text from citation (default: False).",
        "model": "The search model to use ('exa' or 'exa-pro').",
    },
    strict=False,
    name="exa_answer",
)
def exa_answer(
    query: str,
    text: bool = False,
    model: Optional[str] = None,
) -> str:
    """
    Get an LLM answer to a question informed by Exa search results.

    Returns:
        str: A JSON-formatted string containing the generated answer and its citations.
    """
    api_key = getenv("EXA_API_KEY")
    if not api_key:
        return "Error: EXA_API_KEY not set."
    if model and model not in ["exa", "exa-pro"]:
        return "Error: Model must be either 'exa' or 'exa-pro'."
    exa = Exa(api_key)
    answer_kwargs = {"model": model, "text": text}
    answer_kwargs = {k: v for k, v in answer_kwargs.items() if v is not None}
    try:
        answer_response = exa.answer(query=query, **answer_kwargs)
        result = {
            "answer": answer_response.answer,
            "citations": [
                {
                    "id": citation.id,
                    "url": citation.url,
                    "title": citation.title,
                    "published_date": citation.published_date,
                    "author": citation.author,
                    "text": citation.text if text else None,
                }
                for citation in answer_response.citations
            ],
        }
        result_json = json.dumps(result, indent=4)

        return result_json
    except Exception as e:
        return f"Error: {e}"
