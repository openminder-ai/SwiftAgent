from typing import (
    get_type_hints,
    Union,
    get_origin,
    get_args,
    Callable,
    Dict,
    Any,
    Optional,
    List,
)


def python_type_to_json_schema(py_type: Any) -> dict:
    """
    Converts a Python type annotation into a JSON Schema fragment.

    Supports basic types, unions (including Optionals), lists and dictionaries.
    """
    origin = get_origin(py_type)

    if origin is Union:
        # Filter out NoneType for optionals
        args = [t for t in get_args(py_type) if t is not type(None)]
        if len(args) == 1:
            return python_type_to_json_schema(args[0])
        else:
            # For more complex unions, we return an anyOf list of possible schemas.
            return {"anyOf": [python_type_to_json_schema(arg) for arg in args]}

    elif origin in (list, List):
        # For lists, use "array" type with items schema.
        # If no type is specified, default to string items.
        item_types = get_args(py_type)
        item_type = item_types[0] if item_types else str
        return {"type": "array", "items": python_type_to_json_schema(item_type)}

    elif origin in (dict, Dict):
        # For dictionaries, we assume keys are strings (as per JSON standard).
        # We support a value type if provided, defaulting to string otherwise.
        args = get_args(py_type)
        value_type = args[1] if len(args) > 1 else str
        return {
            "type": "object",
            "additionalProperties": python_type_to_json_schema(value_type),
        }

    # Base types mapping
    elif py_type == str:
        return {"type": "string"}
    elif py_type == int:
        return {"type": "integer"}
    elif py_type == float:
        return {"type": "number"}
    elif py_type == bool:
        return {"type": "boolean"}

    # Fallback to string if type is unknown
    return {"type": "string"}
