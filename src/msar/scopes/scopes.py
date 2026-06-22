from collections import defaultdict
from typing import Iterable
from functools import reduce


class Scope:
    def __init__(self, names: Iterable[str] | str):
        if isinstance(names, str):
            self.names = [names]
        else:
            self.names = list(names)
    
    @property
    def scope_names(self):
        return set(self.names)

    def expand(self, scope_names: set[str]) -> dict[str, set[str]]:
        ...


class Admin(Scope):
    '''Admin scopes have access to every other specified scope'''

    def expand(self, scope_names):
        return {name: scope_names for name in self.names}


class Basic(Scope):
    def expand(self, scope_names):
        return {name: {name} for name in self.names}


class Hierarchy(Scope):
    '''
    Iterable(a, b, c)
    - a has access to {a, b, c}
    - b has access to {b, c}
    - c has access to {c}
    '''
    
    def expand(self, scope_names):
        exp = {}
        hierarchy = set()

        for name in reversed(self.names):
            hierarchy.add(name)

            exp[name] = hierarchy.copy()
        
        return exp
