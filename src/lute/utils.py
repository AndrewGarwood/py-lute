"""
*`@file`* `utils`
"""
from __future__ import annotations
from pathlib import (Path, PurePath)
from datetime import (datetime, date, time)
from collections.abc import Collection, Mapping
from typing import (Any, Callable, Iterable, Literal, Optional)
from random import sample as random_sample
import sys


INDENT_LOG_LINE = f'\n\t • '
""" = `'\\n\\t • '` """
SPACES_PER_INDENT = 4
SIMPLE_INDENT = (" " * SPACES_PER_INDENT) + "> "

def indented_line(indent_count: int=1, /):
    return "\n" + " " * (SPACES_PER_INDENT * indent_count)

def count_leading_spaces(s: str, /) -> int:
    return count_leading_char(s, char=" ")

def count_leading_char(s: str, /, char: str) -> int:
    return len(s) - len(s.lstrip(char))


def get_frame(depth: int=1, /): # sys._getframe is expensive/slow, so maybe I shouldn't use this...
    """
    get stack frame at specified depth using `sys._getframe`
    - e.g. `depth = 1` → the direct caller of `get_frame`
    """
    try: return sys._getframe(depth)
    except Exception as e: return f"<unknown frame>({depth=}) _getframe error: {e}"

def callsite(
    depth: int=1, 
    *info: Any,
    include_lineno: bool=False,
    file_info: Literal['name', 'stem', 'full']='stem',
    _sep: str="."
):
    """
    *`@returns`* `f"[{_file_info}{_sep}{_func_info}({_caller_detail})]"`
    
    Inspects stack frame at specified depth to build callsite signature using `sys._getframe`
    - e.g. `depth = 1` → the direct caller of `callsite` 
    """
    _caller_detail = f' {", ".join(str(x) for x in info)} ' if info else ''
    try: frame = sys._getframe(depth)
    except Exception: return f"<unknown frame>({depth=}, {info=})"
    code = frame.f_code
    func = code.co_name
    path = Path(code.co_filename)
    lineno = frame.f_lineno
    cls_type = (
        type(frame.f_locals["self"]) 
        if "self" in frame.f_locals
        else frame.f_locals["cls"] 
        if ("cls" in frame.f_locals and isinstance(frame.f_locals["cls"], type))
        else None  
    )
    cls_name: Optional[str]= cls_type.__name__ if cls_type else None
    _func_info = f"{cls_name}.{func}" if cls_name else func
    _file_info = (
        getattr(path, file_info, f"<{file_info} unknown>") 
        if file_info in ('name', 'stem') 
        else str(path)
    )
    if (include_lineno): _file_info = f"{_file_info}{lineno}"
    return f"[{_file_info}{_sep}{_func_info}({_caller_detail})]"

_SCAN_LIMIT = 8
_MAX_REPR_LEN = 128
def _scan_type(items: Iterable[Any], max_scan: int=4) -> str:
    item_types = list(set([type(x).__name__ for x in items]))
    n = len(item_types)
    if (n == 1): 
        return item_types[0]
    return " | ".join(random_sample(item_types, k=min(n, max_scan)))

def annotate(
    value: Any, 
    /, 
    sample_size: int=4, 
    placeholder: str="Unknown", 
    square_brackets: bool=False
) -> str:
    """ 
    *`@param`* `sample_size (uint) 0 <= _SCAN_LIMIT = 8`
        - used when `value` is a `Collection` to sample its elements' types 
    
    *`@returns`* `info (str)`
    - `'{value.__name__} <{type}>'` if `value` is `Callable`
    - `'{value.isoformat()} <{type}>'` if `value` is `(date, datetime, time)`
    - `'{value} <{type}>'` if `value` is `(int, float, bool, None)`
    - `'{value[:_MAX_REPR_LEN]} {type}<{T}>({size})'` if `value` is `(str, bytes, bytearray)`
    - `'{type}'` if `value` is not a `Collection`
    - `'{type}<{K}, {V}>({size})'` if `value` is `Mapping<K, V>`
    - `'{type}<{T}>({size})'` if `value` is `Iterable<T>`
    - `'{type}<{placeholder}>({size})'` otherwise
    """
    left, right = ("[", "]") if square_brackets else ("<", ">")
    name = type(value).__name__
    if (isinstance(value, Callable)):
        return f"{value.__name__} {left}{name}{right}"
    if (isinstance(value, (date, datetime, time))):
        return f"{value.isoformat()} {left}{name}{right}"
    if (isinstance(value, (Path, PurePath))):
        pathstr = str(value)
        size = len(pathstr)
        _repr = (
            pathstr if size <= _MAX_REPR_LEN
            else f". . .{pathstr[size-_MAX_REPR_LEN:]}"
        )
        return f"'{_repr}' {left}{name}{right}"
    if (isinstance(value, (int, float, bool, type(None)))):
        return f"{value} {left}{name}{right}"
    if (not isinstance(value, Collection)): 
        return name
    size = len(value)
    if (isinstance(value, (str, bytes, bytearray))):
        _repr = (
            value if size <= _MAX_REPR_LEN
            else f"{value[:_MAX_REPR_LEN]}. . ."
        )
        return f"'{_repr}' {left}{name}{right}({size})"
    result = "".join([name, left, "{}", right, f"({size})"])
    if (sample_size < 0): 
        sample_size = abs(sample_size)
    if (size and sample_size > size):
        sample_size = min(_SCAN_LIMIT, (sample_size % size))
    if (isinstance(value, Mapping)):
        if (size and sample_size):
            k = _scan_type(value.keys(), sample_size) or placeholder
            v = _scan_type(value.values(), sample_size) or placeholder
        else:
            k, v = placeholder, placeholder
        return result.format(f"{k}, {v}")
    if (isinstance(value, Iterable)):
        if (not size or not sample_size):
            return result.format(placeholder)
        return result.format(_scan_type(value, sample_size))
    return result.format(placeholder)