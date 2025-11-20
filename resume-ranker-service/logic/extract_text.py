import PyPDF2
from io import BytesIO
from typing import Optional


def extract_text_from_pdf(pdf_content: bytes) -> str:
    """
    Extract text from PDF file content.
    
    Args:
        pdf_content: PDF file as bytes
        
    Returns:
        Extracted text as string
    """
    try:
        pdf_file = BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {str(e)}")

