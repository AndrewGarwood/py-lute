"""
*`@file`* `lute/_warnings`

`WarningManager`
"""

from typing import (TypedDict, Literal, TypeAlias)
import warnings

WarningAction: TypeAlias = Literal['ignore', 'once'] | str

class WarningFilters(TypedDict): # Record<WarningReaction, Any> , total=False
    ignore: set[str]
    once: set[str]

class WarningManager():
    """
    ```
    - @property def filters(cls) -> WarningFilters # Record<str, set[str]>
    @classmethod def ignore(cls, *message: str)
    @classmethod def clear(cls, *action: WarningAction)
    @classmethod def remove_filter(cls, action: WarningAction, *message: str)
    ```
    """
    _filters = WarningFilters(ignore=set(), once=set())

    @classmethod
    def ignore(cls, *message: str):
        for s in message:
            warnings.filterwarnings('ignore', message=s)
            cls._filters['ignore'].add(s)

    @classmethod
    def clear(cls, *action: WarningAction):
        """ `0` args → clear all """
        if (not action):
            action = tuple(cls._filters.keys())
        for a in action:
            if (hasattr(cls._filters, a)): 
                cls._filters[a].clear()
        return None

    @classmethod
    def remove_filter(cls, action: WarningAction, *message: str) -> None:
        if (action not in cls._filters): return None
        for s in message:
            if (s not in cls._filters[action]): continue
            cls._filters[action].remove(s)

    @property
    def filters(cls):
        return cls._filters