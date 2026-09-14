from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ExtractedChunk:
    sequence_number: int
    content: str
    page_number: int | None = None


@dataclass
class ExtractionResult:
    extraction_method: str
    chunks: list[ExtractedChunk]


class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, file_bytes: bytes) -> ExtractionResult:
        pass