"""Base type for future direct scrapers."""

from abc import ABC, abstractmethod
from typing import List

from ..models import Flight


class BaseScraper(ABC):
    """Subclass to implement airline or OTA-specific scraping (advanced / self-hosted)."""

    @abstractmethod
    def search(self, origin: str, destination: str, date: str) -> List[Flight]:
        raise NotImplementedError
