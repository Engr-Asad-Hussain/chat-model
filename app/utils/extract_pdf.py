import io

from PyPDF2 import PdfReader


def extract_text_from_pdf(file_content: bytes) -> bytes:
    with io.BytesIO(file_content) as f:
        reader = PdfReader(f)
        page = reader.pages[0]
        return page.extract_text().encode("utf-8")
