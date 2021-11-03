"""
General utilities.
"""
from enum import Enum, unique
import logging
from dataclasses import dataclass


@unique
class LoggingLevel(Enum):
    DEBUG = str(logging.DEBUG)
    INFO = str(logging.INFO)
    WARNING = str(logging.WARNING)
    ERROR = str(logging.ERROR)
    CRITICAL = str(logging.CRITICAL)


@unique
class OutputType(Enum):
    JSON = "JSON"
    RICH = "RICH"


@dataclass
class QueryResults:
    score: float
    text: str
    title: str
    published: str
    publication: str
    entry: str
    id: str
    reference: str
