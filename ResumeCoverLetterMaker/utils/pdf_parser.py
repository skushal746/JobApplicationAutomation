"""
src/pdf_parser.py

Extracts plain text from a PDF file stored in assets/.
"""

from pypdf import PdfReader


def extract_text_from_pdf(path: str) -> str:
    """
    Read a PDF from `path` and return all its text as a single string.

    Args:
        path: Relative or absolute path to the PDF file.

    Returns:
        Concatenated text content from all pages.

    Raises:
        FileNotFoundError: If the PDF does not exist at the given path.
    """
    reader = PdfReader(path)
    pages_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)
    return "\n".join(pages_text)
