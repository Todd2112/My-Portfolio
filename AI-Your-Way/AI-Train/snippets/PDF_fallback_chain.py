# Demonstrates: Intelligent fallback chain for PDF extraction.
# Engineering judgment: don't fail on bad input, degrade gracefully through
# three increasingly expensive extraction methods until one succeeds.
# Part of ai-train.py. Not standalone.

def extract_pdf_with_fallback(file_bytes: bytes) -> str:
    """
    Tries three extraction methods in order of quality vs. cost:

    1. pdfplumber  — table-aware, best for structured text PDFs
                     rejected if is_extraction_garbled() returns True
    2. pytesseract — OCR for scanned/image-based PDFs
                     only invoked if pdfplumber output is garbled or fails
    3. PyPDF2      — basic text extraction, last resort
                     no quality check, accepted if non-empty

    Raises RuntimeError only if all three methods fail or produce garbled output.
    """
    text = ""

    # Attempt 1: pdfplumber (structured extraction)
    if pdfplumber:
        try:
            text = extract_pdf_with_structure(file_bytes)
            if not is_extraction_garbled(text):
                return text  # accept — clean output
            # reject — garbled, fall through to OCR
            text = ""
        except Exception:
            pass

    # Attempt 2: OCR (scanned PDFs)
    if OCR_AVAILABLE and not text:
        try:
            text = extract_pdf_with_ocr(file_bytes)
            return text  # OCR output accepted if no exception
        except Exception:
            pass

    # Attempt 3: PyPDF2 (basic fallback)
    if PyPDF2 and not text:
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            pages = [page.extract_text() for page in reader.pages if page.extract_text()]
            text = "\n".join(pages)
            if text.strip():
                return text
        except Exception:
            pass

    if not text or is_extraction_garbled(text):
        raise RuntimeError("PDF extraction failed — file may be corrupted or encrypted")

    return text
