"""
Enhanced Document Processing

OCR, table extraction, summarization, and multi-language support.
"""
import os
from typing import Dict, List, Optional
from openai import OpenAI
from cost import CostTracker

# Initialize cost tracker
cost_tracker = CostTracker()

# Try to import OCR libraries
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from langdetect import detect
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False


class DocumentProcessor:
    """Enhanced document processing with OCR and analysis"""
    
    def __init__(self):
        """Initialize document processor"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=api_key)
    
    def extract_text_with_ocr(self, image_path: str, language: Optional[str] = None) -> Dict:
        """
        Extract text from image using OCR.
        
        Args:
            image_path: Path to image file
            language: Optional language code (e.g., 'eng', 'fra')
            
        Returns:
            Dict with extracted text and metadata
        """
        if not OCR_AVAILABLE:
            raise Exception("OCR not available. Install pytesseract and PIL.")
        
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang=language or 'eng')
            
            return {
                "text": text,
                "language": language or "eng",
                "word_count": len(text.split()),
                "char_count": len(text)
            }
        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")
    
    def extract_tables(self, pdf_path: str) -> Dict:
        """
        Extract tables from PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dict with extracted tables
        """
        if not PDFPLUMBER_AVAILABLE:
            raise Exception("PDF table extraction not available. Install pdfplumber.")
        
        try:
            tables = []
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    for table_num, table in enumerate(page_tables):
                        tables.append({
                            "page": page_num + 1,
                            "table_number": table_num + 1,
                            "data": table,
                            "row_count": len(table),
                            "col_count": len(table[0]) if table else 0
                        })
            
            return {
                "tables": tables,
                "table_count": len(tables)
            }
        except Exception as e:
            raise Exception(f"Table extraction failed: {str(e)}")
    
    def detect_language(self, text: str) -> str:
        """Detect language of text"""
        if not LANGDETECT_AVAILABLE:
            return "unknown"
        
        try:
            return detect(text)
        except:
            return "unknown"
    
    def summarize_document(self, text: str, max_length: int = 300, user_id: str = "default") -> Dict:
        """
        Summarize document using LLM.
        
        Args:
            text: Document text
            max_length: Maximum summary length
            user_id: User identifier
            
        Returns:
            Dict with summary and metadata
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"Summarize the following document in {max_length} words or less. Focus on key points and main ideas."
                    },
                    {
                        "role": "user",
                        "content": text[:10000]  # Limit to first 10K chars
                    }
                ],
                max_tokens=max_length
            )
            
            summary = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            # Track cost
            cost = cost_tracker.estimate_cost(tokens_used, "gpt-4o")
            cost_tracker.update_budget(user_id, cost, "document_summarization")
            
            return {
                "summary": summary,
                "original_length": len(text),
                "summary_length": len(summary),
                "tokens_used": tokens_used,
                "cost": cost
            }
        except Exception as e:
            raise Exception(f"Document summarization failed: {str(e)}")
    
    def categorize_document(self, text: str, user_id: str = "default") -> Dict:
        """
        Automatically categorize and tag document.
        
        Args:
            text: Document text
            user_id: User identifier
            
        Returns:
            Dict with category and tags
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze this document and return a JSON object with 'category' (one word) and 'tags' (array of 3-5 relevant tags)."
                    },
                    {
                        "role": "user",
                        "content": text[:5000]  # Limit to first 5K chars
                    }
                ],
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            tokens_used = response.usage.total_tokens if response.usage else 0
            cost = cost_tracker.estimate_cost(tokens_used, "gpt-4o")
            cost_tracker.update_budget(user_id, cost, "document_categorization")
            
            return {
                **result,
                "tokens_used": tokens_used,
                "cost": cost
            }
        except Exception as e:
            raise Exception(f"Document categorization failed: {str(e)}")


# Global document processor instance
document_processor = DocumentProcessor()

