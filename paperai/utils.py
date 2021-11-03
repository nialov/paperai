"""
General utilities.
"""
import logging
from dataclasses import dataclass
from enum import Enum, unique


@unique
class LoggingLevel(Enum):

    """
    Logging level enums.
    """

    DEBUG = str(logging.DEBUG)
    INFO = str(logging.INFO)
    WARNING = str(logging.WARNING)
    ERROR = str(logging.ERROR)
    CRITICAL = str(logging.CRITICAL)


@unique
class OutputType(Enum):

    """
    Output type enums.
    """

    JSON = "JSON"
    RICH = "RICH"


@dataclass
class QueryResults:

    """
    Query result dataclass.
    """

    score: float
    text: str
    title: str
    published: str
    publication: str
    entry: str
    id: str
    reference: str
