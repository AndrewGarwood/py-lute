"""
*`@file`* `lute/message.py`
"""
from __future__ import annotations
from pathlib import Path
import sys, json
import traceback
from typing import (Any, Optional, TypeVar)
import re

E = TypeVar("E", bound=BaseException)

INDENT_LOG_LINE = f'\n\t • '
""" = `'\\n\\t • '` """
SPACES_PER_INDENT = 4
SIMPLE_INDENT = (" " * SPACES_PER_INDENT) + "> "

def _indented_line(indent_count: int=1, /):
    return "\n" + " " * (SPACES_PER_INDENT * indent_count)

def _leading_spaces(s: str, /) -> int:
    return _count_leading_chars(s, char=" ")

def _count_leading_chars(s: str, /, char: str=" ") -> int:
    return len(s) - len(s.lstrip(char))

def bad_arg(value: Any, name: str, reason: str, *expected: str | type):
    _expected = tuple(
        x if isinstance(x, str) 
        else str(x.__name__) if hasattr(x, "__name__") 
        else str(x) 
        for x in expected
    )
    return (
        f"{reason} for arg '{name}'",
        f"expected: {' | '.join(_expected)}",
        f"received: type({name})={type(value)} {value=}"
    )

class LogMessage():
    _messages: list[str]
    _sep: str
    kwargs: dict[str, Any]
    
    @property
    def message(self) -> str:
        return self._sep.join(self._messages)
    
    def __init__(
        self, 
        *message: str | Any, 
        _sep: Optional[str]=None, 
        _body_offset_indents: int=2, 
        **kwargs
    ):
        self._messages = [str(m) for m in message if m is not None]
        if (not _sep):
            head = self._messages[0] if self._messages else ""
            num_spaces = _leading_spaces(head) if head else 0
            head_indent_count = num_spaces // SPACES_PER_INDENT if num_spaces > 4 else 0
            _sep = _indented_line(head_indent_count + _body_offset_indents)
        self._sep = _sep
        self.kwargs = kwargs
    
    @classmethod
    def err(
        cls, 
        error: BaseException, 
        *args, 
        _traceback_limit: int=0, 
        **kwargs
    ):
        _args: list[str] = []
        _kwargs: dict[str, Any] = {}
        if (_traceback_limit > 0):
            kwargs["traceback"] = "".join(
                traceback.TracebackException.from_exception(error, limit=_traceback_limit).format()
            )
        if ("error" not in kwargs):
            _kwargs["error"] = f"({type(error).__name__}) {str(error)}"
        remaining_args: list[str] = []
        for a in args:
            if not isinstance(a, str):
                remaining_args.append(str(a))
                continue
            m = re.match(r"^(?P<key>.+)\s*(:|=)\s+(?P<value>.+)$", a)
            if not m:
                remaining_args.append(a)
                continue
            d = m.groupdict()
            _kwargs.update({d["key"]: d["value"]})

        _kwargs.update(kwargs)
        _args.extend(remaining_args)
        _heading = f"Failed: {type(error)}"
        return cls(_heading, *_args, **_kwargs)
    
    
    
    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.message:
            result["message"] = self.message
        for key, value in self.kwargs.items():
            if isinstance(value, LogMessage):
                result[key] = value.to_dict()
            elif isinstance(value, Path):
                result[key] = str(value)
            # elif isinstance(value, (date, datetime)) -> isoformat()
            else:
                result[key] = value
        return result
    
    def _format(self, indent: int = 4) -> str:
        pad = " " * indent
        lines = [self.message] #INDENT_LOG_LINE.split(self.message) if INDENT_LOG_LINE in self.message else [self.message]
        for key, value in self.kwargs.items():
            if hasattr(value, "_format"):
                lines.append(f"{pad}{key}:")
                lines.append(value._format(indent))
            else:
                lines.append(f"{pad}{key}: {str(value)}")
        return _indented_line(1).join(lines)
    
    def __repr__(self): return self.__str__()

    def __str__(self): return self._format()
    
LogMsg = LogMessage


