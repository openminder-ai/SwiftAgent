from typing import TypeAlias, Protocol, Callable, Union, List
import numpy as np
from functools import wraps
from chromadb import Documents, EmbeddingFunction, Embeddings

SwiftEmbedder: TypeAlias = EmbeddingFunction


class SingleEmbedFunction(Protocol):
    def __call__(self, text: str) -> np.ndarray | list[float]: ...


def embedder(func: SingleEmbedFunction) -> SwiftEmbedder:
    # Create a function that will become our instance method
    def wrapped_call(self, input: Documents) -> Embeddings:
        if isinstance(input, str):
            return [func(input)]
        return [func(doc) for doc in input]

    # Create the wrapper class without trying to use @wraps
    class WrappedEmbeddingFunction(EmbeddingFunction):
        # Attach the metadata from original function if needed
        __name__ = func.__name__
        __doc__ = func.__doc__
        __module__ = func.__module__

        # Define call method
        __call__ = wrapped_call

    # Return an instance
    return WrappedEmbeddingFunction()
