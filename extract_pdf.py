#!/usr/bin/env python3
"""
PDF Text Extraction Script for Medical Emergencies Section 01
Extracts text content from PDF to integrate into the nursing chatbot
"""

try:
    import PyPDF2
    import pdfplumber
    EXTRACTION_AVAILABLE = True
except ImportError:
    EXTRACTION_AVAILABLE = False

import os

def extract_text_pypdf2(pdf_path):
    """Extract text using PyPDF2"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error with PyPDF2: {e}")
        return None

def extract_text_pdfplumber(pdf_path):
    """Extract text using pdfplumber (better for complex layouts)"""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text += f"\n--- Page {page_num + 1} ---\n"
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        return text
    except Exception as e:
        print(f"Error with pdfplumber: {e}")
        return None

def main():
    pdf_path = "Section 01 - Medical Emergencies.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        print("\nPlease ensure the file 'Section 01 - Medical Emergencies.pdf' is in the current directory.")
        return False
    
    if not EXTRACTION_AVAILABLE:
        print("📦 PDF extraction libraries not available.")
        print("To install required libraries, run:")
        print("  pip install PyPDF2 pdfplumber")
        print("\nAlternatively, you can:")
        print("1. Open the PDF file manually")
        print("2. Copy the text content") 
        print("3. Save it as 'medical_emergencies_content.txt'")
        print("4. I'll then integrate it into the chatbot")
        return False
    
    print("📄 Extracting text from 'Section 01 - Medical Emergencies.pdf'...")
    print("=" * 60)
    
    # Try pdfplumber first (better for complex layouts)
    text = extract_text_pdfplumber(pdf_path)
    
    if not text or len(text.strip()) < 100:
        print("⚠️ pdfplumber extraction yielded minimal content, trying PyPDF2...")
        text = extract_text_pypdf2(pdf_path)
    
    if text and len(text.strip()) > 100:
        # Save extracted text
        output_file = "medical_emergencies_extracted.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"✅ Text successfully extracted and saved to '{output_file}'")
        print(f"📊 Extracted {len(text)} characters from {pdf_path}")
        
        # Show preview
        preview = text[:500] + "..." if len(text) > 500 else text
        print(f"\n📋 Preview of extracted content:")
        print("-" * 40)
        print(preview)
        print("-" * 40)
        
        print(f"\n🔄 Next steps:")
        print(f"1. Review the extracted content in '{output_file}'")
        print(f"2. I'll integrate this content into the chatbot's knowledge base")
        print(f"3. The chatbot will use this as the authoritative Medical Emergencies reference")
        
        return True
    else:
        print("❌ Failed to extract text from PDF")
        print("\nAlternative options:")
        print("1. Convert PDF to text manually and save as 'medical_emergencies_content.txt'")
        print("2. Copy-paste the content and provide it directly")
        return False

if __name__ == "__main__":
    main()
