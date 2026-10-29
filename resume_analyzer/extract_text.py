import os

try:  # pypdf is the maintained successor of PyPDF2; support either.
    from pypdf import PdfReader
except ImportError:  # pragma: no cover
    from PyPDF2 import PdfReader


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF resume. Raises ValueError for unreadable files."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Resume file not found: {pdf_path}")
    if not pdf_path.lower().endswith(".pdf"):
        raise ValueError("Only PDF resume files are supported.")
    try:
        with open(pdf_path, "rb") as handle:
            reader = PdfReader(handle)
            pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as error:  # noqa: BLE001
        raise ValueError(f"Unable to read the PDF: {error}") from error
    text = "\n".join(p for p in pages if p.strip()).strip()
    if not text:
        raise ValueError("No readable text was found. Scanned PDFs are not supported; "
                         "export your resume as a text-based PDF.")
    return text
