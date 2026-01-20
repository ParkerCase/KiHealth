#!/usr/bin/env python3
"""
Analyze paywalled PDF articles and assess for inclusion in top 314 articles.
Extracts content, assesses PROBAST, calculates relevance, and provides recommendations.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    try:
        import pdfplumber
        PDF_AVAILABLE = True
        USE_PDFPLUMBER = True
    except ImportError:
        PDF_AVAILABLE = False
        USE_PDFPLUMBER = False

from scripts.relevance_scoring import RelevanceScorer
from scripts.probast_assessment import PROBASTAssessment
from scripts.factor_extraction import FactorExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> Dict[str, str]:
    """Extract text from PDF file"""
    text = ""
    metadata = {}
    
    if not PDF_AVAILABLE:
        logger.error("PDF extraction library not available. Install PyPDF2 or pdfplumber.")
        return {"text": "", "metadata": {}}
    
    try:
        # Try pdfplumber first (better extraction), fallback to PyPDF2
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                # Extract text from all pages
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                # Extract metadata
                if pdf.metadata:
                    metadata = {
                        "title": pdf.metadata.get("Title", ""),
                        "author": pdf.metadata.get("Author", ""),
                        "subject": pdf.metadata.get("Subject", ""),
                        "creator": pdf.metadata.get("Creator", ""),
                    }
        except ImportError:
            # Fallback to PyPDF2
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                for page_num, page in enumerate(pdf_reader.pages):
                    text += page.extract_text() + "\n"
                
                # Extract metadata
                if pdf_reader.metadata:
                    metadata = {
                        "title": pdf_reader.metadata.get("/Title", ""),
                        "author": pdf_reader.metadata.get("/Author", ""),
                        "subject": pdf_reader.metadata.get("/Subject", ""),
                        "creator": pdf_reader.metadata.get("/Creator", ""),
                    }
        
        return {"text": text, "metadata": metadata}
    
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {e}")
        return {"text": "", "metadata": {}}


def extract_pmid_from_filename(filename: str) -> Optional[str]:
    """Try to extract PMID from filename or metadata"""
    # Common patterns: PMID in filename, DOI in filename, etc.
    # For now, return None - will need to match with database
    return None


def analyze_pdf_article(pdf_path: str, relevance_scorer: RelevanceScorer, 
                       probast_assessor: PROBASTAssessment,
                       factor_extractor: FactorExtractor) -> Dict:
    """Analyze a single PDF article"""
    filename = os.path.basename(pdf_path)
    logger.info(f"Analyzing: {filename}")
    
    # Extract text
    extraction_result = extract_text_from_pdf(pdf_path)
    full_text = extraction_result["text"]
    metadata = extraction_result["metadata"]
    
    if not full_text or len(full_text) < 100:
        logger.warning(f"Insufficient text extracted from {filename}")
        return {
            "filename": filename,
            "status": "error",
            "error": "Insufficient text extracted"
        }
    
    # Extract title and abstract (first 2000 chars often contain this)
    title = metadata.get("title", "")
    abstract_start = full_text.find("Abstract") or full_text.find("ABSTRACT")
    if abstract_start > 0:
        abstract = full_text[abstract_start:abstract_start+2000]
    else:
        abstract = full_text[:2000]  # Use first 2000 chars as abstract
    
    # Create article dict for assessment
    article = {
        "title": title or filename,
        "abstract": abstract,
        "full_text": full_text,
        "journal": "",  # Will try to extract from text
        "pmid": extract_pmid_from_filename(filename),
        "metadata": metadata
    }
    
    # Try to extract journal from text
    journal_patterns = [
        r"Journal of ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+\([0-9]{4}\)",
    ]
    import re
    for pattern in journal_patterns:
        match = re.search(pattern, full_text[:5000])
        if match:
            article["journal"] = match.group(1)
            break
    
    # Calculate relevance score
    relevance_score = relevance_scorer.calculate_relevance_score(article)
    
    # PROBAST assessment
    probast_result = probast_assessor.assess_article(article)
    
    # Extract factors
    try:
        factors = factor_extractor.extract_statistical_associations(full_text)
        factors_count = len(factors)
    except Exception as e:
        logger.warning(f"Error extracting factors: {e}")
        factors = []
        factors_count = 0
    
    # Determine usability
    domain_scores = [
        probast_result.get("domain_1_participants", "Unclear"),
        probast_result.get("domain_2_predictors", "Unclear"),
        probast_result.get("domain_3_outcome", "Unclear"),
        probast_result.get("domain_4_analysis", "Unclear"),
    ]
    
    low_count = domain_scores.count("Low")
    moderate_count = domain_scores.count("Moderate")
    high_count = domain_scores.count("High")
    
    # Usability criteria
    usable = False
    justification = ""
    
    if high_count > 0:
        usable = False
        justification = "Contains High Risk domain(s)"
    elif low_count == 4:
        usable = True
        justification = "All 4 domains Low Risk"
    elif low_count == 3 and moderate_count == 1:
        usable = True
        justification = "3 Low + 1 Moderate (standard PROBAST practice)"
    elif low_count == 2 and moderate_count == 2:
        usable = True
        justification = "2 Low + 2 Moderate (strong justification)"
    elif low_count == 1 and moderate_count == 3:
        usable = True
        justification = "1 Low + 3 Moderate (very strong justification)"
    else:
        usable = False
        justification = "Insufficient Low/Moderate domains"
    
    # Quality score (for ranking)
    quality_score = (
        relevance_score * 0.4 +  # 40% relevance
        (low_count * 25 + moderate_count * 15) * 0.3 +  # 30% PROBAST
        50 * 0.2 +  # 20% study design (assume good if we have full text)
        50 * 0.1  # 10% impact
    )
    
    return {
        "filename": filename,
        "title": title or filename,
        "journal": article.get("journal", "Unknown"),
        "relevance_score": relevance_score,
        "probast_assessment": probast_result,
        "domain_scores": domain_scores,
        "low_count": low_count,
        "moderate_count": moderate_count,
        "high_count": high_count,
        "usable": usable,
        "justification": justification,
        "quality_score": quality_score,
        "factors_extracted": factors_count,
        "factors": factors[:10] if factors else [],  # Top 10 factors
        "text_length": len(full_text),
        "status": "success"
    }


def main():
    """Main analysis function"""
    # Path to PDF directory
    pdf_dir = Path("/Users/parkercase/DOC/data/paywalled-articles-1-12-26")
    
    if not pdf_dir.exists():
        logger.error(f"Directory not found: {pdf_dir}")
        return
    
    # Initialize assessors
    relevance_scorer = RelevanceScorer()
    probast_assessor = PROBASTAssessment()
    factor_extractor = FactorExtractor()
    
    # Get all PDFs
    pdf_files = list(pdf_dir.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files")
    
    # Analyze each PDF
    results = []
    for pdf_path in pdf_files:
        try:
            result = analyze_pdf_article(
                str(pdf_path),
                relevance_scorer,
                probast_assessor,
                factor_extractor
            )
            results.append(result)
        except Exception as e:
            logger.error(f"Error analyzing {pdf_path}: {e}")
            results.append({
                "filename": pdf_path.name,
                "status": "error",
                "error": str(e)
            })
    
    # Sort by quality score
    results.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
    
    # Generate report
    usable_articles = [r for r in results if r.get("usable", False)]
    high_quality = [r for r in results if r.get("quality_score", 0) >= 65]
    high_relevance = [r for r in results if r.get("relevance_score", 0) >= 40]
    
    report = {
        "analysis_date": datetime.now().isoformat(),
        "total_pdfs": len(pdf_files),
        "successfully_analyzed": len([r for r in results if r.get("status") == "success"]),
        "usable_articles": len(usable_articles),
        "high_quality_articles": len(high_quality),
        "high_relevance_articles": len(high_relevance),
        "recommendations": {
            "add_to_top_314": [],
            "consider_for_addition": [],
            "do_not_add": []
        },
        "articles": results
    }
    
    # Categorize recommendations
    for result in results:
        if result.get("status") != "success":
            report["recommendations"]["do_not_add"].append({
                "filename": result.get("filename"),
                "reason": result.get("error", "Analysis failed")
            })
            continue
        
        quality = result.get("quality_score", 0)
        usable = result.get("usable", False)
        relevance = result.get("relevance_score", 0)
        
        if usable and quality >= 65 and relevance >= 40:
            report["recommendations"]["add_to_top_314"].append({
                "filename": result.get("filename"),
                "title": result.get("title"),
                "quality_score": quality,
                "relevance_score": relevance,
                "justification": result.get("justification"),
                "factors_count": result.get("factors_extracted", 0)
            })
        elif usable and relevance >= 40:
            report["recommendations"]["consider_for_addition"].append({
                "filename": result.get("filename"),
                "title": result.get("title"),
                "quality_score": quality,
                "relevance_score": relevance,
                "justification": result.get("justification"),
                "factors_count": result.get("factors_extracted", 0)
            })
        else:
            report["recommendations"]["do_not_add"].append({
                "filename": result.get("filename"),
                "title": result.get("title"),
                "reason": f"Quality: {quality:.1f}, Usable: {usable}, Relevance: {relevance:.1f}"
            })
    
    # Save report
    output_path = Path(__file__).parent.parent / "data" / "paywalled_analysis_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*80)
    print("PAYWALLED PDF ANALYSIS REPORT")
    print("="*80)
    print(f"\nTotal PDFs analyzed: {len(pdf_files)}")
    print(f"Successfully analyzed: {report['successfully_analyzed']}")
    print(f"Usable articles: {len(usable_articles)}")
    print(f"High quality (≥65): {len(high_quality)}")
    print(f"High relevance (≥40): {len(high_relevance)}")
    
    print("\n" + "-"*80)
    print("RECOMMENDATIONS")
    print("-"*80)
    
    print(f"\n✅ ADD TO TOP 314 ({len(report['recommendations']['add_to_top_314'])} articles):")
    for article in report['recommendations']['add_to_top_314']:
        print(f"  • {article['filename']}")
        print(f"    Quality: {article['quality_score']:.1f}, Relevance: {article['relevance_score']:.1f}")
        print(f"    {article['justification']}")
    
    print(f"\n⚠️  CONSIDER FOR ADDITION ({len(report['recommendations']['consider_for_addition'])} articles):")
    for article in report['recommendations']['consider_for_addition']:
        print(f"  • {article['filename']}")
        print(f"    Quality: {article['quality_score']:.1f}, Relevance: {article['relevance_score']:.1f}")
    
    print(f"\n❌ DO NOT ADD ({len(report['recommendations']['do_not_add'])} articles):")
    for article in report['recommendations']['do_not_add'][:10]:  # Show first 10
        print(f"  • {article['filename']}: {article.get('reason', 'N/A')}")
    
    print(f"\n\nFull report saved to: {output_path}")
    print("="*80)
    
    return report


if __name__ == "__main__":
    main()
