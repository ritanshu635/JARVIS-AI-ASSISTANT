#!/usr/bin/env python3
"""
PDF Reader Module for JARVIS
Handles PDF reading with text extraction and OCR fallback
"""

import os
import PyPDF2
import pytesseract
from PIL import Image
import fitz  # PyMuPDF for better PDF handling
import io
import glob
from typing import Optional, List
from engine.command import speak

class PDFReader:
    """PDF reading functionality with OCR fallback"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
        # Common search directories
        self.search_directories = [
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Downloads"),
            "C:/Users/*/Desktop",
            "C:/Users/*/Documents", 
            "C:/Users/*/Downloads"
        ]
    
    def find_pdf(self, filename: str) -> Optional[str]:
        """Find PDF file by name in common directories"""
        print(f"🔍 Searching for PDF: {filename}")
        
        # Clean filename
        filename = filename.lower().strip()
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        # Search in common directories
        for directory in self.search_directories:
            try:
                # Expand wildcards in path
                expanded_dirs = glob.glob(directory)
                for expanded_dir in expanded_dirs:
                    if os.path.exists(expanded_dir):
                        # Search for exact match
                        pdf_path = os.path.join(expanded_dir, filename)
                        if os.path.exists(pdf_path):
                            print(f"✅ Found PDF: {pdf_path}")
                            return pdf_path
                        
                        # Search for partial match
                        for file in os.listdir(expanded_dir):
                            if file.lower().endswith('.pdf') and filename.replace('.pdf', '') in file.lower():
                                pdf_path = os.path.join(expanded_dir, file)
                                print(f"✅ Found PDF (partial match): {pdf_path}")
                                return pdf_path
            except (PermissionError, FileNotFoundError):
                continue
        
        print(f"❌ PDF not found: {filename}")
        return None
    
    def extract_text_pypdf2(self, pdf_path: str) -> str:
        """Extract text using PyPDF2"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                print(f"📄 PDF has {len(reader.pages)} pages")
                
                for page_num, page in enumerate(reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += f"\n--- Page {page_num} ---\n{page_text}\n"
                    print(f"✅ Extracted text from page {page_num}")
            
            return text.strip()
        except Exception as e:
            print(f"❌ PyPDF2 extraction failed: {e}")
            return ""
    
    def extract_text_ocr(self, pdf_path: str) -> str:
        """Extract text using OCR (fallback for scanned PDFs)"""
        try:
            print("🔍 Attempting OCR extraction...")
            text = ""
            
            # Convert PDF to images and OCR
            pdf_document = fitz.open(pdf_path)
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                
                # Convert to PIL Image
                image = Image.open(io.BytesIO(img_data))
                
                # OCR the image
                page_text = pytesseract.image_to_string(image)
                if page_text.strip():
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                print(f"✅ OCR extracted text from page {page_num + 1}")
            
            pdf_document.close()
            return text.strip()
        except Exception as e:
            print(f"❌ OCR extraction failed: {e}")
            return ""
    
    def read_pdf(self, filename: str) -> Optional[str]:
        """Main method to read PDF with fallback strategies"""
        try:
            # Find the PDF file
            pdf_path = self.find_pdf(filename)
            if not pdf_path:
                return None
            
            print(f"📖 Reading PDF: {os.path.basename(pdf_path)}")
            speak(f"Found and reading PDF: {os.path.basename(pdf_path)}")
            
            # Try PyPDF2 first
            text = self.extract_text_pypdf2(pdf_path)
            
            # If no text extracted, try OCR
            if not text or len(text.strip()) < 50:
                print("📸 PDF appears to be scanned, trying OCR...")
                speak("This appears to be a scanned PDF, using optical character recognition")
                text = self.extract_text_ocr(pdf_path)
            
            if text and len(text.strip()) > 10:
                print(f"✅ Successfully extracted {len(text)} characters")
                return text
            else:
                print("❌ No readable text found in PDF")
                return None
                
        except Exception as e:
            print(f"❌ Error reading PDF: {e}")
            return None
    
    def chunk_text_for_speech(self, text: str, max_chunk_size: int = 500) -> List[str]:
        """Break text into manageable chunks for speech"""
        if not text:
            return []
        
        # Split by sentences first
        sentences = text.replace('\n', ' ').split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) < max_chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def read_pdf_aloud(self, filename: str, max_chunks: int = 10) -> bool:
        """Read PDF and speak it aloud in chunks"""
        try:
            text = self.read_pdf(filename)
            if not text:
                speak(f"Sorry, I couldn't find or read the PDF named {filename}")
                return False
            
            # Break into chunks
            chunks = self.chunk_text_for_speech(text)
            
            if not chunks:
                speak("The PDF appears to be empty or unreadable")
                return False
            
            # Limit chunks to prevent extremely long reading
            if len(chunks) > max_chunks:
                speak(f"This PDF is quite long. I'll read the first {max_chunks} sections. You can ask me to continue later.")
                chunks = chunks[:max_chunks]
            
            speak(f"Starting to read the PDF. It has {len(chunks)} sections.")
            
            # Read each chunk
            for i, chunk in enumerate(chunks, 1):
                print(f"\n📖 Reading section {i}/{len(chunks)}")
                speak(f"Section {i}.")
                speak(chunk)
                
                # Small pause between sections
                import time
                time.sleep(1)
            
            speak("Finished reading the PDF")
            return True
            
        except Exception as e:
            print(f"❌ Error reading PDF aloud: {e}")
            speak("I encountered an error while reading the PDF")
            return False