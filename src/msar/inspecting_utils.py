from inspect import signature, iscoroutinefunction
from fastapi import Request

from .tokens import AccessToken


def get_request_name(func):
    '''Get name of the parameter with annotation fastapi.Request'''
     
    sign = signature(func)
    pass_request_name = None

    for param in sign.parameters.values():
        if param.annotation is Request:
            pass_request_name = param.name

            break
    
    return pass_request_name


def get_access_name(func):
    '''Get name of the parameter with annotation msar.AccessToken'''

    sign = signature(func)
    pass_access_name = None

    for param in sign.parameters.values():
        if param.annotation is AccessToken:
            pass_access_name = param.name

            break
    
    return pass_access_name


def is_async(func):
    return iscoroutinefunction(func)
