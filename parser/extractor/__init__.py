"""
Extractor module
"""
from __future__ import annotations
from abc import ABC, abstractmethod
import functools


class Extractor(ABC):
    """Base Extractor"""

    def __init__(self, data: str) -> None:
        self._data = data

    @abstractmethod
    def extract(self):
        """extract signature"""            
