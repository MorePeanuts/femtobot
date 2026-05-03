from dataclasses import dataclass

from langchain.tools import BaseTool, tool
from langgraph.types import interrupt
from tavily import TavilyClient


@dataclass
class SearchResult:
    search_query: str
    title: str
    url: str
    content: str
    score: float | None = None

    def to_dict(self) -> dict:
        return {
            'search_query': self.search_query,
            'title': self.title,
            'url': self.url,
            'content': self.content,
            'score': self.score,
        }


_tavily_client = None


@tool('WebSearch')
def tavily_search(search_query: str) -> list[SearchResult]:
    """
    This is a tool for conducting web searches using Tavily.

    Args:
        search_query: Questions that need to be queried
    """
    global _tavily_client
    if _tavily_client is None:
        try:
            _tavily_client = TavilyClient()
        except Exception:
            raise

    results = []
    try:
        response = _tavily_client.search(
            query=search_query,
            max_results=5,
            include_raw_content=True,
            timeout=240,
        )

        for item in response.get('results', []):
            result = SearchResult(
                search_query=search_query,
                title=item.get('title'),
                url=item.get('url'),
                content=item.get('content'),
                score=item.get('score'),
            )
            results.append(result)
    except Exception:
        raise

    return results


_builtin_tools = {
    tavily_search.name: tavily_search,
}


def get_builtin_tool(tool_name) -> BaseTool:
    return _builtin_tools[tool_name]


def get_builtin_tool_list() -> list[BaseTool]:
    return list(_builtin_tools.values())
