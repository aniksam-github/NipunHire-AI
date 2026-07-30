"""
PDF Service — PyMuPDF (fitz) integration for text & layout extraction from PDF resumes.
"""

import fitz  # PyMuPDF
import logging

logger = logging.getLogger(__name__)


class PDFExtractionError(ValueError):
    """Raised when a PDF cannot provide usable machine-readable text."""


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> tuple[str, int]:
    """
    Opens PDF bytes using PyMuPDF and extracts clean concatenated text.

    Returns:
        tuple[str, int]: (extracted_text, page_count)
    """
    doc = None
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_count = len(doc)
        text_content: list[str] = []

        for page in doc:
            # Extract plain text with layout preservation
            page_text = page.get_text("text")
            if page_text:
                text_content.append(page_text)

        full_text = "\n".join(text_content).strip()
        if not full_text:
            raise PDFExtractionError(
                "PDF contains no extractable text; upload a text-based PDF rather than a scanned image."
            )
        logger.info("Extracted %d characters across %d pages via PyMuPDF", len(full_text), page_count)
        return full_text, page_count

    except PDFExtractionError:
        raise
    except Exception as exc:
        logger.error("PyMuPDF PDF extraction failed: %s", exc)
        raise PDFExtractionError("Could not read PDF file. File may be corrupted or encrypted.") from exc

    finally:
        if doc is not None:
            doc.close()
