import docx2txt
import pypdf
import re


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF resume using pypdf.
    Handles multi-page PDFs and cleans extracted text.
    """
    try:
        reader = pypdf.PdfReader(file_path)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"

        return clean_resume_text(text)

    except Exception as e:
        raise RuntimeError(f"Error reading PDF file: {e}")


def extract_text_from_docx(file_path: str) -> str:
    """
    Extracts text from a DOCX resume using docx2txt.
    """
    try:
        text = docx2txt.process(file_path)
        return clean_resume_text(text)

    except Exception as e:
        raise RuntimeError(f"Error reading DOCX file: {e}")


def extract_text_from_txt(file_path: str) -> str:
    """
    Extracts text from plain TXT resumes.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return clean_resume_text(text)

    except Exception as e:
        raise RuntimeError(f"Error reading TXT file: {e}")


def clean_resume_text(text: str) -> str:
    """
    Cleans extracted text:
    - Removes extra whitespace
    - Normalizes line breaks
    - Removes repeating blank lines
    """
    if not text:
        return ""

    # Remove weird unicode characters
    text = re.sub(r"[^\S\r\n]+", " ", text)

    # Replace multiple newlines with a single newline
    text = re.sub(r"\n\s*\n+", "\n", text)

    # Strip leading/trailing spaces
    text = text.strip()

    return text


def extract_resume_text(file_path: str) -> str:
    """
    Main function — detects file type and extracts text accordingly.
    Supported formats: PDF, DOCX, TXT.
    """

    file_path = file_path.lower()

    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)

    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)

    elif file_path.endswith(".txt"):
        return extract_text_from_txt(file_path)

    else:
        raise ValueError("Unsupported file format. Use PDF, DOCX, or TXT.")

