from typing import (
    get_type_hints,
    Union,
    get_origin,
    get_args,
    Callable,
    Dict,
    Any,
    Optional,
)


def python_type_to_json_type(
    py_type,
):
    """
    Converts a Python type annotation into a JSON Schema type.
    E.g. str -> 'string', int -> 'integer', float -> 'number', bool -> 'boolean', ...
    You can expand or customize as needed.
    """
    if get_origin(py_type) is Union:
        # Usually means optional or union of different types
        args = [t for t in get_args(py_type) if t is not type(None)]
        if len(args) == 1:
            return python_type_to_json_type(args[0])
        else:
            # More complex union: you could return multiple "type" variants
            # e.g. {"anyOf": [...]} or default to "string"
            return "string"
    if py_type == str:
        return "string"
    elif py_type == int:
        return "integer"
    elif py_type == float:
        return "number"
    elif py_type == bool:
        return "boolean"
    # Fallback
    return "string"
