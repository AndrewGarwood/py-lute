"""
*`@file`* `config`
"""
from __future__ import annotations
import logging
from enum import IntEnum
from pathlib import Path
from typing import (Any, Literal, Optional, TypeAlias,)
from rich.logging import (RichHandler)

StrPath: TypeAlias = str | Path

class LogManager():
    """
    *`@description`* manage logging output files
    ```
    _outdir: Path = Path("logs")
    _file_registry: dict[str, Path] = {}
    ```
    """
    _outdir: Path = Path("logs")
    """ root dir where all log files live """
    _file_registry: dict[str, Path] = {}
    """ map logical key to path relative from `_outdir` """
    
    @classmethod
    def set_outdir(cls, path: StrPath, /) -> None:
        cls._outdir = Path(path)
        
    @classmethod
    def register_alias(cls, key: str, relative_path: StrPath, /) -> None:
        cls._file_registry[key] = Path(relative_path)
        
    @classmethod
    def resolve_path(cls, target: StrPath, /) -> Path:
        """
        *`@param`* `target (str | Path)` 
            - a key of `cls._file_registry` or a path relative to `cls._outdir` 
        *`@returns`* `resolved (Path)`
            - `cls._outdir` joined with relative path `if target is not absolute`
        
        """
        rel_path: Path | None = None
        if (isinstance(target, str) and target in cls._file_registry):
            rel_path = cls._file_registry[target]
        else:
            rel_path = Path(target)
        if (rel_path.is_absolute()): 
            return rel_path
        resolved = cls._outdir.joinpath(rel_path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        return resolved

class LogLevel(IntEnum):
    """
    `Literal[0, 10, 20, 30, 40, 50]`
    """
    CRITICAL = logging.CRITICAL
    FATAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET

DEFAULT_MESSAGE_FORMAT = "[%(name)s.%(funcName)s] %(message)s"
DEFAULT_DATE_FORMAT = "[%X]"

def get_logger(
    name: str,
    /,
    level: LogLevel = LogLevel.DEBUG,
    file: Optional[StrPath]=None,
    console: bool=True,
    fmt:str=DEFAULT_MESSAGE_FORMAT,
    datefmt:str=DEFAULT_DATE_FORMAT,
    use_existing: bool=True,
    rich_kwargs: dict[str, Any] = {
        "rich_tracebacks": True,
        "show_path": False,
        "tracebacks_show_locals": False,
    }
) -> logging.Logger:
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if (use_existing and logger.hasHandlers()): 
        return logger
    
    if (logger.hasHandlers()):
        if (use_existing): 
            return logger
        for h in logger.handlers:
            logger.removeHandler(h)
    
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
    
    if (console):
        console_hnd = RichHandler(**rich_kwargs)
        console_hnd.setLevel(level)
        console_hnd.setFormatter(formatter)
        logger.addHandler(console_hnd)
    
    if (file):
        outpath = LogManager.resolve_path(file)
        file_hnd = logging.FileHandler(
            outpath, 
            mode='a',
            encoding='utf-8'
        )
        file_hnd.setFormatter(formatter)
        file_hnd.setLevel(level)
        logger.addHandler(file_hnd)
        
    return logger


def attach_file_handler(
    logger: logging.Logger, 
    path: StrPath, 
    /,
    level: LogLevel = LogLevel.DEBUG,
    fmt:str=DEFAULT_MESSAGE_FORMAT,
    datefmt:str=DEFAULT_DATE_FORMAT,
    mode: Literal['a', 'w']='a',
    require_singular: bool=True,
    strict: bool=True
) -> None:
    if (logger.hasHandlers() and (strict or require_singular)):
        for h in logger.handlers:
            if (not isinstance(h, logging.FileHandler)): continue
            if (strict):
                raise RuntimeError(f"logger {logger.name} already has file handler")
            if (require_singular):
                logger.removeHandler(h)
    
    outpath = LogManager.resolve_path(path)
    h = logging.FileHandler(outpath, mode=mode, encoding="utf-8")
    h.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
    h.setLevel(level)
    logger.addHandler(h)
    return None