from ..database import add_document_chunk, update_document_status
from ..extractors.registry import ExtractorRegistry


class DocumentProcessor:
    def __init__(self, registry: ExtractorRegistry | None = None):
        self.registry = registry or ExtractorRegistry()

    def process(
        self,
        document_id: str,
        filename: str,
        file_bytes: bytes,
    ):
        try:
            extractor = self.registry.get_extractor(filename)
            result = extractor.extract(file_bytes)

            if not result.chunks:
                raise ValueError("No extractable content found")

            for chunk in result.chunks:
                add_document_chunk(
                    document_id=document_id,
                    sequence_number=chunk.sequence_number,
                    page_number=chunk.page_number,
                    content=chunk.content,
                )

            update_document_status(
                document_id=document_id,
                status="completed",
                extraction_method=result.extraction_method,
            )

        except Exception as exc:
            update_document_status(
                document_id=document_id,
                status="failed",
                error_message=str(exc),
            )
            return