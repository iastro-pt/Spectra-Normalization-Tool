from __future__ import annotations
import numpy as np
from typing import Iterable, Any


def json_ready_converter(value: Any) -> Any:
    """Convert a given value to a json-serializable format."""
    if isinstance(value, np.ndarray):
        value = value.tolist()
    elif isinstance(value, dict):
        value = {i: json_ready_converter(j) for i, j in value.items()}
    elif isinstance(value, list):
        value = [json_ready_converter(i) for i in value]
    elif isinstance(value, Iterable):
        value = np.asarray(value).tolist()

    return value


def process_dictionary(dictionary: dict[str, Any]) -> dict[str, Any]:
    """Convert every entry of a dictionary to be json-serializable."""
    new_dict = {}
    for key, value in dictionary.items():
        if isinstance(value, dict):
            new_dict[key] = process_dictionary(value)
        else:
            new_dict[key] = json_ready_converter(value)
    return new_dict
