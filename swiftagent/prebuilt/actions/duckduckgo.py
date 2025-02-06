import json
from typing import Any, Optional

from swiftagent.actions.set import ActionSet

try:
    from duckduckgo_search import DDGS
except ImportError:
    raise ImportError(
        "`duckduckgo-search` not installed. Please install using `pip install duckduckgo-search`"
    )

duckduckgo_actions = ActionSet(
    name="duckduckgo",
    description="DuckDuckGo toolkit actions for search and news",
)


@duckduckgo_actions.action(
    params={
        "query": "The query to search for.",
        "max_results": "The maximum number of results to return (default: 5).",
        "modifier": "An optional modifier to prepend to the query.",
        "fixed_max_results": "A fixed number of maximum results (overrides max_results if provided).",
        "headers": "Headers to be used in the search request.",
        "proxy": "Proxy to be used in the search request.",
        "proxies": "A list of proxies to be used in the search request.",
        "timeout": "The maximum number of seconds to wait for a response (default: 10).",
        "verify_ssl": "Whether to verify SSL (default: True).",
    },
    strict=False,
)
def duckduckgo_search(
    query: str,
    max_results: int = 5,
    modifier: Optional[str] = None,
    fixed_max_results: Optional[int] = None,
    headers: Optional[Any] = None,
    proxy: Optional[str] = None,
    proxies: Optional[Any] = None,
    timeout: Optional[int] = 10,
    verify_ssl: bool = True,
) -> str:
    """
    Use this function to search DuckDuckGo for a query.

    Args:
        query(str): The query to search for.
        max_results (optional, default=5): The maximum number of results to return.

    Returns:
        The result from DuckDuckGo.
    """
    ddgs = DDGS(
        headers=headers,
        proxy=proxy,
        proxies=proxies,
        timeout=timeout,
        verify=verify_ssl,
    )
    effective_max_results = (
        fixed_max_results if fixed_max_results is not None else max_results
    )
    if not modifier:
        results = ddgs.text(keywords=query, max_results=effective_max_results)
    else:
        results = ddgs.text(
            keywords=f"{modifier} {query}", max_results=effective_max_results
        )
    return json.dumps(results, indent=2)


@duckduckgo_actions.action(
    params={
        "query": "The query to search for.",
        "max_results": "The maximum number of results to return (default: 5).",
        "fixed_max_results": "A fixed number of maximum results (overrides max_results if provided).",
        "headers": "Headers to be used in the search request.",
        "proxy": "Proxy to be used in the search request.",
        "proxies": "A list of proxies to be used in the search request.",
        "timeout": "The maximum number of seconds to wait for a response (default: 10).",
        "verify_ssl": "Whether to verify SSL (default: True).",
    },
    strict=False,
)
def duckduckgo_news(
    query: str,
    max_results: int = 5,
    fixed_max_results: Optional[int] = None,
    headers: Optional[Any] = None,
    proxy: Optional[str] = None,
    proxies: Optional[Any] = None,
    timeout: Optional[int] = 10,
    verify_ssl: bool = True,
) -> str:
    """
    Use this function to get the latest news from DuckDuckGo.

    Args:
        query(str): The query to search for.
        max_results (optional, default=5): The maximum number of results to return.

    Returns:
        The latest news from DuckDuckGo.
    """
    ddgs = DDGS(
        headers=headers,
        proxy=proxy,
        proxies=proxies,
        timeout=timeout,
        verify=verify_ssl,
    )
    effective_max_results = (
        fixed_max_results if fixed_max_results is not None else max_results
    )
    results = ddgs.news(keywords=query, max_results=effective_max_results)
    return json.dumps(results, indent=2)
