#!/usr/bin/env python3
"""
Analyze PDF articles for OA prediction relevance
Requires: pip install pdfplumber (or PyPDF2)
"""
import sys
import os
import re

def extract_pdf(filename):
    """Extract text from PDF"""
    # Try pdfplumber first
    try:
        import pdfplumber
        with pdfplumber.open(filename) as pdf:
            return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    except ImportError:
        pass
    
    # Try PyPDF2
    try:
        import PyPDF2
        with open(filename, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    except ImportError:
        pass
    
    return None

def analyze_article(text, title):
    """Analyze article for OA prediction relevance"""
    if not text:
        return {"error": "Could not extract text"}
    
    analysis = {
        "title": title,
        "key_findings": [],
        "predictive_factors": [],
        "methodology": "",
        "sample_size": "",
        "outcome_measures": [],
        "statistical_results": [],
        "relevance_to_model": "",
        "recommendations": []
    }
    
    # Extract key sections
    abstract_match = re.search(r'(?i)abstract[:\s]*(.*?)(?=\n\n|\n[A-Z][A-Z\s]+:)', text, re.DOTALL)
    if abstract_match:
        abstract = abstract_match.group(1)[:2000]
        analysis["abstract"] = abstract
    
    # Find predictive factors
    factor_patterns = [
        r'(?i)(predictor|risk factor|prognostic factor|associated with)[:\s]+([^\.]+)',
        r'(?i)(hazard ratio|HR|odds ratio|OR)[:\s]*([0-9.]+)',
        r'(?i)(BMI|body mass index|age|sex|gender|WOMAC|KOOS|KL grade|Kellgren)',
    ]
    
    for pattern in factor_patterns:
        matches = re.findall(pattern, text[:50000])  # Search first 50k chars
        if matches:
            analysis["predictive_factors"].extend([str(m) for m in matches[:10]])
    
    # Find statistical results
    stat_patterns = [
        r'(?i)(AUC|C-statistic|area under curve)[:\s]*([0-9.]+)',
        r'(?i)(p\s*[<>=]\s*[0-9.]+|p\s*=\s*[0-9.]+)',
        r'(?i)(95%\s*CI|confidence interval)[:\s]*([0-9.]+\s*[-–]\s*[0-9.]+)',
    ]
    
    for pattern in stat_patterns:
        matches = re.findall(pattern, text[:50000])
        if matches:
            analysis["statistical_results"].extend([str(m) for m in matches[:10]])
    
    # Sample size
    sample_match = re.search(r'(?i)(n\s*=\s*[0-9,]+|sample size[:\s]*[0-9,]+|participants[:\s]*[0-9,]+)', text[:20000])
    if sample_match:
        analysis["sample_size"] = sample_match.group(0)
    
    # Outcome measures
    outcome_patterns = [
        r'(?i)(WOMAC|KOOS|total knee replacement|TKR|arthroplasty|progression)',
    ]
    for pattern in outcome_patterns:
        matches = re.findall(pattern, text[:50000])
        if matches:
            analysis["outcome_measures"].extend(list(set(matches))[:10])
    
    return analysis

def main():
    files = [
        ('Inter-Limb Strength Asymmetry and Risk of Total Knee Replacement_A Survival Analysis.pdf',
         'Inter-Limb Strength Asymmetry and Risk of Total Knee Replacement'),
        ('keaf686.pdf', 'Article 2 (keaf686)'),
        ('Physical Activity and 4-Year Radiographic Medial Joint Space Loss in Knee Osteoarthritis_A Joint Model Analysis.pdf',
         'Physical Activity and 4-Year Radiographic Medial Joint Space Loss')
    ]
    
    print("="*80)
    print("OA PREDICTION ARTICLE ANALYSIS")
    print("="*80)
    print()
    
    for filename, title in files:
        if not os.path.exists(filename):
            print(f"⚠️  File not found: {filename}\n")
            continue
        
        print(f"\n{'='*80}")
        print(f"ARTICLE: {title}")
        print('='*80)
        
        text = extract_pdf(filename)
        if not text:
            print("❌ Could not extract text. Please install: pip install pdfplumber")
            print("   Or provide text version of the article.\n")
            continue
        
        analysis = analyze_article(text, title)
        
        print(f"\n📊 SAMPLE SIZE: {analysis.get('sample_size', 'Not found')}")
        print(f"\n🔍 PREDICTIVE FACTORS FOUND:")
        for factor in analysis.get('predictive_factors', [])[:15]:
            print(f"   - {factor}")
        
        print(f"\n📈 STATISTICAL RESULTS:")
        for result in analysis.get('statistical_results', [])[:10]:
            print(f"   - {result}")
        
        print(f"\n📋 OUTCOME MEASURES:")
        outcomes = list(set(analysis.get('outcome_measures', [])))
        for outcome in outcomes[:10]:
            print(f"   - {outcome}")
        
        if 'abstract' in analysis:
            print(f"\n📄 ABSTRACT (excerpt):")
            print(analysis['abstract'][:500] + "...")
        
        print("\n")

if __name__ == "__main__":
    main()


