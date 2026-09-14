from pathlib import Path

from .base import BaseExtractor
from .docx import DocxExtractor
from .pdf import PdfExtractor
from ..services.ocr import MockOCRService


class ExtractorRegistry:
    def __init__(self):
        ocr_service = MockOCRService()

        self.extractors: dict[str, BaseExtractor] = {
            ".pdf": PdfExtractor(ocr_service),
            ".docx": DocxExtractor(),
        }

    def get_extractor(self, filename: str) -> BaseExtractor:
        extension = Path(filename).suffix.lower()

        extractor = self.extractors.get(extension)

        if extractor is None:
            raise ValueError(
                f"Unsupported document type: {extension or 'unknown'}"
            )

        return extractor