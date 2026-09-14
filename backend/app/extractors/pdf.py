from io import BytesIO

from pypdf import PdfReader

from .base import BaseExtractor, ExtractedChunk, ExtractionResult
from ..services.ocr import BaseOCRService


MIN_MEANINGFUL_TEXT_LENGTH = 20


class PdfExtractor(BaseExtractor):
    def __init__(self, ocr_service: BaseOCRService):
        self.ocr_service = ocr_service

    def extract(self, file_bytes: bytes) -> ExtractionResult:
        reader = PdfReader(BytesIO(file_bytes))

        chunks = []
        total_text_length = 0

        for page_number, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()

            if not text:
                continue

            total_text_length += len(text)

            chunks.append(
                ExtractedChunk(
                    sequence_number=len(chunks) + 1,
                    page_number=page_number,
                    content=text,
                )
            )

        if total_text_length >= MIN_MEANINGFUL_TEXT_LENGTH:
            return ExtractionResult(
                extraction_method="digital_pdf",
                chunks=chunks,
            )

        ocr_text = self.ocr_service.extract_text(file_bytes)

        return ExtractionResult(
            extraction_method="mock_ocr",
            chunks=[
                ExtractedChunk(
                    sequence_number=1,
                    content=ocr_text,
                )
            ],
        )