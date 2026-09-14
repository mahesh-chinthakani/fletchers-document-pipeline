from io import BytesIO

from docx import Document

from .base import BaseExtractor, ExtractedChunk, ExtractionResult


class DocxExtractor(BaseExtractor):
    def extract(self, file_bytes: bytes) -> ExtractionResult:
        document = Document(BytesIO(file_bytes))

        chunks = []
        sequence_number = 1

        for paragraph in document.paragraphs:
            text = paragraph.text.strip()

            if not text:
                continue

            chunks.append(
                ExtractedChunk(
                    sequence_number=sequence_number,
                    content=text,
                )
            )

            sequence_number += 1

        return ExtractionResult(
            extraction_method="docx",
            chunks=chunks,
        )