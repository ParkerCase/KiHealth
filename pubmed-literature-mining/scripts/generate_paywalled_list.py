#!/usr/bin/env python3
"""
Generate a clean list of paywalled articles for sharing with doctors.
Outputs a simple text file with journal names, titles, and PMIDs.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.file_storage import FileStorage


def generate_paywalled_list(output_file: str = "PAYWALLED_ARTICLES.txt", threshold: int = 70):
    """
    Generate a clean list of paywalled articles
    
    Args:
        output_file: Output file path
        threshold: Minimum relevance score
    """
    storage = FileStorage()
    
    # Get paywalled articles
    paywalled = storage.get_paywalled_articles(threshold=threshold)
    
    # Sort by relevance score (highest first)
    paywalled_sorted = sorted(
        paywalled, 
        key=lambda x: x.get('relevance_score', 0), 
        reverse=True
    )
    
    # Generate output
    lines = []
    lines.append("=" * 80)
    lines.append("PAYWALLED ARTICLES - KNEE OA PROGRESSION")
    lines.append("=" * 80)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Total Articles: {len(paywalled_sorted)}")
    lines.append(f"Relevance Threshold: {threshold}/100")
    lines.append("")
    lines.append("=" * 80)
    lines.append("")
    
    # Group by journal for easier review
    journals = {}
    for article in paywalled_sorted:
        journal = article.get('journal', 'Unknown Journal')
        if journal not in journals:
            journals[journal] = []
        journals[journal].append(article)
    
    # Sort journals by number of articles
    journals_sorted = sorted(
        journals.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )
    
    # Output by journal
    for journal, articles in journals_sorted:
        lines.append(f"\n{'=' * 80}")
        lines.append(f"JOURNAL: {journal}")
        lines.append(f"Articles: {len(articles)}")
        lines.append(f"{'=' * 80}\n")
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'No title')
            pmid = article.get('pmid', 'N/A')
            score = article.get('relevance_score', 0)
            doi = article.get('doi', '')
            authors = article.get('authors', '')
            pub_date = article.get('publication_date', '')
            
            lines.append(f"{i}. {title}")
            lines.append(f"   PMID: {pmid}")
            if doi:
                lines.append(f"   DOI: {doi}")
            if authors:
                lines.append(f"   Authors: {authors}")
            if pub_date:
                lines.append(f"   Published: {pub_date[:10] if len(pub_date) >= 10 else pub_date}")
            lines.append(f"   Relevance Score: {score}/100")
            lines.append(f"   PubMed Link: https://pubmed.ncbi.nlm.nih.gov/{pmid}/")
            lines.append("")
    
    # Also create a simple CSV for easy import
    csv_lines = []
    csv_lines.append("Journal,Title,PMID,DOI,Relevance Score,PubMed Link")
    for article in paywalled_sorted:
        journal = article.get('journal', 'Unknown').replace(',', ';')
        title = article.get('title', 'No title').replace(',', ';').replace('\n', ' ')
        pmid = article.get('pmid', 'N/A')
        doi = article.get('doi', '')
        score = article.get('relevance_score', 0)
        pubmed_link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        
        csv_lines.append(f'"{journal}","{title}",{pmid},"{doi}",{score},"{pubmed_link}"')
    
    # Write text file
    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    # Write CSV file
    csv_path = output_path.with_suffix('.csv')
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(csv_lines))
    
    print(f"✅ Generated paywalled articles list:")
    print(f"   - Text file: {output_path}")
    print(f"   - CSV file: {csv_path}")
    print(f"   - Total articles: {len(paywalled_sorted)}")
    print(f"   - Journals: {len(journals_sorted)}")
    
    return output_path, csv_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate paywalled articles list')
    parser.add_argument(
        '--output', 
        default='PAYWALLED_ARTICLES.txt',
        help='Output file path (default: PAYWALLED_ARTICLES.txt)'
    )
    parser.add_argument(
        '--threshold',
        type=int,
        default=70,
        help='Minimum relevance score (default: 70)'
    )
    
    args = parser.parse_args()
    
    generate_paywalled_list(args.output, args.threshold)

