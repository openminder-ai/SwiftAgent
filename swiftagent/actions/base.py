from typing import Any, Callable, Optional, get_type_hints
from functools import wraps
import inspect

from swiftagent.actions.utils import python_type_to_json_type

class Action:
    def __init__(
        self,
        func: Callable,
        name: str,
        description: Optional[str] = None,
        params: Optional[dict[str, str]] = None,
        strict: bool = True
    ):
        self.func = func
        self.name = name
        self.description = description or func.__doc__ or ""
        self.params = params or {}
        self.strict = strict
        
        # Cache the metadata when instantiated
        self._metadata = self._build_metadata()
        
        # Create the wrapped function with metadata
        self.wrapped_func = self._create_wrapper()

    def _build_metadata(self) -> dict:
        """Builds the function metadata including JSON schema."""
        sig = inspect.signature(self.func)
        type_hints = get_type_hints(self.func)
        props = {}
        required_fields = []

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
                
            param_type = type_hints.get(param_name, str)
            json_type = self._python_type_to_json_type(param_type)
            
            param_description = self.params.get(
                param_name, 
                f"Parameter {param_name}"
            )
            
            props[param_name] = {
                "type": json_type,
                "description": param_description,
            }
            
            if param.default is inspect.Parameter.empty:
                required_fields.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": props,
                    "required": required_fields,
                    "additionalProperties": not self.strict,
                },
                "strict": self.strict,
            },
        }

    def _create_wrapper(self) -> Callable:
        """Creates a wrapped version of the function with metadata attached."""
        @wraps(self.func)
        def wrapper(*args, **kwargs):
            return self.func(*args, **kwargs)
            
        # Attach metadata to the wrapper
        wrapper.__action_metadata__ = self._metadata
        return wrapper

    @staticmethod
    def _python_type_to_json_type(py_type: type) -> str:
        return python_type_to_json_type(py_type)

    @property
    def metadata(self) -> dict:
        """Returns the action's metadata."""
        return self._metadata