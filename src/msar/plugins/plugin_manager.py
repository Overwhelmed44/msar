from fastapi import Request, Response
from collections import defaultdict
from typing import Iterable

from .storages.storage import Storage
from .plugins.plugin import Plugin, HookAt


class PluginManager:
    def __init__(self, plugins: Iterable[Plugin], storage: Storage | None = None):
        self.plugins = list(plugins)

        self.position_mapping: dict[HookAt, list[Plugin]] = defaultdict(list)
        for plugin in self.plugins:
            for ha in plugin.hook_at:
                self.position_mapping[ha].append(plugin)

        self.storage = storage
    
    def before_request(self, request: Request):
        ...
    
    def after_request(self, request: Request, response: Response):
        ...
    
    @classmethod
    def get_default_manager(cls):
        return cls([], None)
