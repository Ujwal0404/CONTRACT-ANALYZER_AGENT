from pathlib import Path
import docx
import PyPDF2
from app.utils import FileParsingError, logger
import re

class ContractParser:
    @staticmethod
    def parse(file_path: str) -> str:
        try:
            file_path = Path(file_path)
            
            if file_path.suffix.lower() == '.pdf':
                return ContractParser._parse_pdf(file_path)
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                return ContractParser._parse_word(file_path)
            else:
                return ContractParser._parse_text(file_path)
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {str(e)}")
            raise FileParsingError(f"Failed to parse file: {str(e)}")

    @staticmethod
    def _parse_pdf(file_path: Path) -> str:
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                # Clean the extracted text
                text = ContractParser._clean_text(text)
                
                if not text.strip():
                    raise FileParsingError("No text content extracted from PDF")
                    
                return text
        except Exception as e:
            raise FileParsingError(f"PDF parsing error: {str(e)}")

    @staticmethod
    def _parse_word(file_path: Path) -> str:
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
            
            # Clean the extracted text
            text = ContractParser._clean_text(text)
            
            if not text.strip():
                raise FileParsingError("No text content extracted from Word document")
                
            return text
        except Exception as e:
            raise FileParsingError(f"Word document parsing error: {str(e)}")

    @staticmethod
    def _parse_text(file_path: Path) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                
            # Clean the extracted text
            text = ContractParser._clean_text(text)
            
            if not text.strip():
                raise FileParsingError("No text content in file")
                
            return text
        except Exception as e:
            raise FileParsingError(f"Text file parsing error: {str(e)}")

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might interfere with JSON
        text = text.replace('\u0000', '')
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        # Remove other problematic characters
        text = ''.join(char for char in text if ord(char) >= 32)
        return text.strip()