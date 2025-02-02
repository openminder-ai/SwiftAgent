from typing import Optional, Any, Callable


def resource(
    name: Optional[str] = None,
    description: Optional[str] = None,
    params: Optional[dict[str, str]] = None,
    strict: bool = True,
    embedder: Optional[Callable] = None,
    vector_store: Optional[Callable] = None,
):
    pass
