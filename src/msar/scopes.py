from collections import defaultdict
from typing import Iterable
from functools import reduce


class Scope:
    def __init__(self, names: Iterable[str]):
        self.names = set(names)

    def expand(self) -> dict[str, set[str]]:
        ...


class Basic(Scope):
    def __init__(self, names: Iterable[str]):
        super().__init__(names)
    
    def expand(self):
        return {name: {name} for name in self.names}


class Hierarchy(Scope):
    '''
    Iterable(a, b, c)
    - a has access to {a}
    - b has access to {a, b}
    - c has access to {a, b, c}
    '''

    def __init__(self, names: Iterable[str]):
        super().__init__(names)
    
    def expand(self):
        exp = {}
        ierarchy = set()

        for name in self.names:
            ierarchy.add(name)

            exp[name] = ierarchy.copy()
        
        return exp


class GlobalScopes:
    def __init__(self, scopes: Iterable[Scope]):
        self.scopes = self.expand_scopes(scopes)
    
    def get_local_scopes(self, names: Iterable[str]) -> set[str]:
        return reduce(lambda a, b: a | b, (self.scopes[k] for k in self.scopes if k in names), set())

    @staticmethod
    def expand_scopes(scopes: Iterable[Scope]) -> dict[str, set[str]]:
        rd = defaultdict(set)

        for scope in scopes:
            for name, value in scope.expand().items():
                rd[name] = rd[name] | value
        
        return rd
