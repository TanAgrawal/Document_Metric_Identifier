import os
import tempfile
import logging as log
from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    CSVLoader,
    UnstructuredFileLoader
)

try:
    from langchain_community.document_loaders import PyMuPDFLoader
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from langchain_community.document_loaders import UnstructuredPDFLoader
    HAS_UNSTRUCTURED_PDF = True
except ImportError:
    HAS_UNSTRUCTURED_PDF = False

try:
    from langchain_community.document_loaders import UnstructuredWordDocumentLoader
    HAS_UNSTRUCTURED_WORD = True
except ImportError:
    HAS_UNSTRUCTURED_WORD = False

try:
    from langchain_community.document_loaders import UnstructuredPowerPointLoader
    HAS_UNSTRUCTURED_PPT = True
except ImportError:
    HAS_UNSTRUCTURED_PPT = False

try:
    from langchain_community.document_loaders import UnstructuredExcelLoader
    HAS_UNSTRUCTURED_EXCEL = True
except ImportError:
    HAS_UNSTRUCTURED_EXCEL = False


def extract_with_pdf_loaders(file_path):
    """Try multiple PDF loaders in order of capability"""
    loaders_to_try = []
    
    if HAS_UNSTRUCTURED_PDF:
        loaders_to_try.append(
            lambda: UnstructuredPDFLoader(file_path, mode="elements", strategy="hi_res")
        )
    
    if HAS_PYMUPDF:
        loaders_to_try.append(lambda: PyMuPDFLoader(file_path))
    
    loaders_to_try.append(lambda: PyPDFLoader(file_path))
    
    for loader_func in loaders_to_try:
        try:
            loader = loader_func()
            documents = loader.load()
            text = "\n\n".join([doc.page_content for doc in documents])
            
            if text and len(text.strip()) > 50:
                return text
        except Exception as e:
            log.debug(f"Loader failed: {e}, trying next...")
            continue
    
    raise Exception("All PDF loaders failed to extract text")


def extract_with_word_loaders(file_path, suffix):
    loaders_to_try = []
    
    if suffix == '.docx':
        loaders_to_try.append(lambda: Docx2txtLoader(file_path))
    
    if HAS_UNSTRUCTURED_WORD:
        loaders_to_try.append(lambda: UnstructuredWordDocumentLoader(file_path))
    
    for loader_func in loaders_to_try:
        try:
            loader = loader_func()
            documents = loader.load()
            text = "\n\n".join([doc.page_content for doc in documents])
            if text and len(text.strip()) > 10:
                return text
        except Exception as e:
            log.debug(f"Word loader failed: {e}, trying next...")
            continue
    
    raise Exception("All Word document loaders failed")


def extract_with_excel_loaders(file_path):
    loaders_to_try = []
    
    if HAS_UNSTRUCTURED_EXCEL:
        loaders_to_try.append(lambda: UnstructuredExcelLoader(file_path))
    
    try:
        import pandas as pd
        df = pd.read_excel(file_path)
        return df.to_string()
    except:
        pass
    
    for loader_func in loaders_to_try:
        try:
            loader = loader_func()
            documents = loader.load()
            text = "\n\n".join([doc.page_content for doc in documents])
            if text:
                return text
        except Exception as e:
            log.debug(f"Excel loader failed: {e}")
            continue
    
    raise Exception("All Excel loaders failed")


def extract_with_ppt_loaders(file_path):
    if HAS_UNSTRUCTURED_PPT:
        try:
            loader = UnstructuredPowerPointLoader(file_path)
            documents = loader.load()
            return "\n\n".join([doc.page_content for doc in documents])
        except Exception as e:
            log.debug(f"PPT loader failed: {e}")
    
    raise Exception("PowerPoint loader failed")


def extract_text_with_tika_client(file_obj, filename=None):

    temp_file_path = None
    
    try:
        suffix = ''
        if filename:
            suffix = Path(filename).suffix.lower()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file_path = temp_file.name
            file_obj.seek(0)
            temp_file.write(file_obj.read())
        
        extracted_text = None
        
        if suffix == '.pdf':
            extracted_text = extract_with_pdf_loaders(temp_file_path)
            
        elif suffix in ['.docx', '.doc']:
            extracted_text = extract_with_word_loaders(temp_file_path, suffix)
            
        elif suffix in ['.xlsx', '.xls']:
            extracted_text = extract_with_excel_loaders(temp_file_path)
            
        elif suffix in ['.pptx', '.ppt']:
            extracted_text = extract_with_ppt_loaders(temp_file_path)
            
        elif suffix == '.txt':
            loader = TextLoader(temp_file_path)
            documents = loader.load()
            extracted_text = "\n\n".join([doc.page_content for doc in documents])
            
        elif suffix == '.csv':
            loader = CSVLoader(temp_file_path)
            documents = loader.load()
            extracted_text = "\n\n".join([doc.page_content for doc in documents])
            
        else:
            log.info(f"Unknown format {suffix}, trying UnstructuredFileLoader")
            loader = UnstructuredFileLoader(temp_file_path)
            documents = loader.load()
            extracted_text = "\n\n".join([doc.page_content for doc in documents])
        
        if not extracted_text or len(extracted_text.strip()) < 10:
            raise Exception("Extracted text is too short or empty")
        
        log.info(f"Successfully extracted {len(extracted_text)} characters from {filename}")
        return extracted_text
        
    except Exception as e:
        log.error(f'Error extracting text: {str(e)}')
        raise Exception(f'Error extracting text from file: {str(e)}')
        
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                log.warning(f"Could not delete temporary file: {e}")