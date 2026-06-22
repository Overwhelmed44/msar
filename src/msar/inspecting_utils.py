from inspect import signature, iscoroutinefunction, Parameter

from typing import Iterable


def get_requested_params(func, annotations: Iterable[type]) -> dict[type, str | None]:
    '''Get names of the parameters with specified annotations'''

    annotations = set(annotations)
    sign = signature(func)
    names: dict[type, str | None] = {
        annotation: None for annotation in annotations
    }

    for param in sign.parameters.values():
        if param.annotation in annotations:
            names[param.annotation] = param.name
    
    return names


def is_async(func):
    return iscoroutinefunction(func)
