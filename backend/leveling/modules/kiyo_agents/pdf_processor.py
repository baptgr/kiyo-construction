import os
import tempfile
import logging
from typing import IO
from django.core.files import File

# Langchain PDF Loader
from langchain_community.document_loaders import PyPDFLoader

logger = logging.getLogger(__name__)

def process_pdf_upload(pdf_file: IO) -> str:
    """Processes uploaded PDF file and extracts text content."""
    if not pdf_file:
        return ""

    #logger.info(f"Processing uploaded PDF: {pdf_file.name}")
    temp_pdf_path = None
    pdf_text_content = ""
    try:
        # Save PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf_path = temp_pdf.name
            for chunk in pdf_file.chunks():
                temp_pdf.write(chunk)
        
        # Use PyPDFLoader to extract text
        loader = PyPDFLoader(temp_pdf_path)
        pages = loader.load() # or load_and_split()
        pdf_text_content = "\n\n".join([page.page_content for page in pages])
        #logger.info(f"Extracted {len(pdf_text_content)} characters from PDF.")

    except Exception as pdf_err:
        logger.error(f"Error processing PDF {pdf_file.name}: {pdf_err}", exc_info=True)
        pdf_text_content = "[Error processing attached PDF]"
    finally:
        # Ensure temporary file is deleted
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            try:
                os.remove(temp_pdf_path)
                #logger.info(f"Deleted temporary PDF file: {temp_pdf_path}")
            except OSError as del_err:
                #logger.error(f"Error deleting temporary PDF file {temp_pdf_path}: {del_err}")
                pass
    
    return pdf_text_content

def process_pdf_file(pdf_path: str) -> str:
    with open(pdf_path, "rb") as f:
        django_file = File(f)
        return process_pdf_upload(django_file)