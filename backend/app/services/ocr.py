from abc import ABC, abstractmethod


class BaseOCRService(ABC):
    @abstractmethod
    def extract_text(self, file_bytes: bytes) -> str:
        pass


class MockOCRService(BaseOCRService):
    def extract_text(self, file_bytes: bytes) -> str:
        return (
            "OCR extraction was required for this scanned PDF. "
            "The external OCR provider is mocked for this assessment."
        )