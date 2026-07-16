class PaperProcessingError(Exception):
    """Base exception for paper-processing failures."""


class InvalidPDFError(PaperProcessingError):
    """Raised when an uploaded file is not a valid PDF."""


class PDFTooLargeError(PaperProcessingError):
    """Raised when a PDF exceeds the configured upload limit."""


class PDFTextExtractionError(PaperProcessingError):
    """Raised when readable text cannot be extracted from a PDF."""
