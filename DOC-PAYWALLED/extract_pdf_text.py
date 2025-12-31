#!/usr/bin/env python3
"""
Extract text from PDFs for analysis
"""
import sys
import os

def extract_with_pdfplumber(filename):
    """Try pdfplumber first"""
    try:
        import pdfplumber
        with pdfplumber.open(filename) as pdf:
            text = ""
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- PAGE {i+1} ---\n{page_text}\n"
            return text
    except ImportError:
        return None
    except Exception as e:
        return f"Error with pdfplumber: {e}"

def extract_with_pypdf2(filename):
    """Fallback to PyPDF2"""
    try:
        import PyPDF2
        with open(filename, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for i, page in enumerate(reader.pages):
                text += f"\n--- PAGE {i+1} ---\n{page.extract_text()}\n"
            return text
    except ImportError:
        return None
    except Exception as e:
        return f"Error with PyPDF2: {e}"

def main():
    files = [
        'Inter-Limb Strength Asymmetry and Risk of Total Knee Replacement_A Survival Analysis.pdf',
        'keaf686.pdf',
        'Physical Activity and 4-Year Radiographic Medial Joint Space Loss in Knee Osteoarthritis_A Joint Model Analysis.pdf'
    ]
    
    for filename in files:
        if not os.path.exists(filename):
            print(f"File not found: {filename}", file=sys.stderr)
            continue
            
        print(f"\n{'='*80}")
        print(f"ARTICLE: {filename}")
        print('='*80)
        
        # Try pdfplumber first
        text = extract_with_pdfplumber(filename)
        if text is None:
            # Try PyPDF2
            text = extract_with_pdfplumber(filename)
            if text is None:
                print("ERROR: Neither pdfplumber nor PyPDF2 available")
                print("Please install: pip install pdfplumber")
                continue
        
        # Print first 25000 characters (key sections)
        print(text[:25000])
        print("\n[... truncated for display ...]\n")

if __name__ == "__main__":
    main()


