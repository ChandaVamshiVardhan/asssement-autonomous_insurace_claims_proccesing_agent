"""
Enhanced PDF-capable Claims Processor
Handles PDF, TXT, and plain text FNOL documents

Author: Vamshi Vardhan
Date: February 6, 2026
"""

import json
import re
from typing import Dict, List, Any, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    import PyPDF2

try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


class PDFClaimsProcessor:
    """Enhanced processor with PDF support"""
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """Extract text from PDF file"""
        if not PDF_SUPPORT:
            raise ImportError("PyPDF2 not installed. Run: pip install PyPDF2")
        
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
        except Exception as e:
            print(f"Error extracting PDF: {e}")
        
        return text
    
    @staticmethod
    def load_document(file_path: str) -> str:
        """Load document from file (PDF or TXT)"""
        path = Path(file_path)
        
        if path.suffix.lower() == '.pdf':
            return PDFClaimsProcessor.extract_text_from_pdf(file_path)
        elif path.suffix.lower() == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    
    @staticmethod
    def process_from_file(file_path: str) -> Dict[str, Any]:
        """Process a claim document from file"""
        from claims_processor import FNOLProcessor
        
        document_text = PDFClaimsProcessor.load_document(file_path)
        processor = FNOLProcessor()
        return processor.process_document(document_text)


def main():
    """Main execution function"""
    processor_module = __import__('claims_processor')
    agent = processor_module.ClaimsProcessingAgent()
    
    # Check for PDF files in the folder
    pdf_files = list(Path('/home/arjun/Downloads/m1').glob('*.pdf'))
    txt_files = list(Path('/home/arjun/Downloads/m1').glob('*.txt'))
    
    print("\n" + "="*70)
    print("AUTONOMOUS INSURANCE CLAIMS PROCESSING AGENT")
    print("="*70)
    
    # Process PDF files first
    for pdf_file in pdf_files:
        if 'FNOL' in pdf_file.name or 'claim' in pdf_file.name.lower():
            try:
                print(f"\nProcessing PDF: {pdf_file.name}")
                text = PDFClaimsProcessor.extract_text_from_pdf(str(pdf_file))
                
                agent.process_claims([{
                    "name": pdf_file.name,
                    "content": text
                }])
            except Exception as e:
                print(f"Error processing {pdf_file.name}: {e}")
    
    # Process TXT files
    for txt_file in txt_files:
        try:
            print(f"\nProcessing TXT: {txt_file.name}")
            with open(txt_file, 'r') as f:
                text = f.read()
            
            agent.process_claims([{
                "name": txt_file.name,
                "content": text
            }])
        except Exception as e:
            print(f"Error processing {txt_file.name}: {e}")
    
    # Export results
    if agent.results:
        agent.export_results('/home/arjun/Downloads/m1/claims_processing_results.json')
    else:
        print("\nNo files processed. Using sample data...")
        # Process sample documents
        from claims_processor import sample_documents
        agent.process_claims(sample_documents)
        agent.export_results('/home/arjun/Downloads/m1/claims_processing_results.json')


if __name__ == "__main__":
    main()
