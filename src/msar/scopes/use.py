from collections import defaultdict
from typing import Iterable
from functools import reduce

from .scopes import Scope


class LocalScopes:
    def __init__(self, scopes: set[str], ignore: bool):
        self.scopes = scopes
        self.ignore = ignore
    
    def __and__(self, scopes: set[str]) -> bool:
        return self.ignore or bool(self.scopes & scopes)


class GlobalScopes:
    def __init__(self, scopes: Iterable[Scope]):
        self.scope_names = self.get_scope_names(scopes)
        self.scopes = self.expand_scopes(scopes)
    
    @staticmethod
    def get_scope_names(scopes: Iterable[Scope]) -> set[str]:
        return reduce(
            lambda a, b: a | b,
            map(lambda s: s.scope_names, scopes),
            set()
        )

    def expand_scopes(self, scopes: Iterable[Scope]) -> dict[str, set[str]]:
        rd = defaultdict(set)

        for scope in scopes:
            for name, value in scope.expand(self.scope_names).items():
                rd[name] |= value
        
        return rd

    def get_local_scopes(self, names: Iterable[str]) -> LocalScopes:
        names = set(names)
        ls = set()

        for user_scope, access_to in self.scopes.items():
            if names & access_to:
                ls.add(user_scope)
        
        return LocalScopes(ls, len(self.scope_names) == 0)
