#!/usr/bin/env python3
"""
Diagnostic script to check what's in Google Sheets and why paywalled articles aren't showing up.
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.google_sheets_storage import get_storage_client

def diagnose():
    """Diagnose paywalled articles issue"""
    print("=" * 80)
    print("PAYWALLED ARTICLES DIAGNOSTIC")
    print("=" * 80)
    
    storage = get_storage_client()
    
    # Check if using Google Sheets
    if not hasattr(storage, 'sheet'):
        print("⚠️  Not using Google Sheets - using file storage")
        print("   This means articles might be in files, not Google Sheets")
        return
    
    try:
        storage._initialize()
        
        # Get all records
        print("\n1. Getting all records from Google Sheets...")
        all_records = storage.sheet.get_all_records()
        print(f"   Total records: {len(all_records)}")
        
        if len(all_records) == 0:
            print("   ⚠️  No records found in Google Sheets!")
            print("   This means articles haven't been saved to Google Sheets yet.")
            return
        
        # Check access types
        print("\n2. Analyzing access types...")
        access_types = {}
        for record in all_records:
            access_type = record.get('access_type', 'unknown')
            access_types[access_type] = access_types.get(access_type, 0) + 1
        
        print("   Access type distribution:")
        for access_type, count in access_types.items():
            print(f"   - {access_type}: {count}")
        
        # Check paywalled articles
        print("\n3. Checking paywalled articles...")
        paywalled_all = [r for r in all_records if r.get('access_type', '').lower() == 'paywalled']
        print(f"   Total paywalled (any score): {len(paywalled_all)}")
        
        # Check with threshold
        paywalled_70 = [r for r in paywalled_all if float(r.get('relevance_score', 0)) >= 70]
        print(f"   Paywalled with score >= 70: {len(paywalled_70)}")
        
        # Show sample paywalled articles
        if paywalled_all:
            print("\n4. Sample paywalled articles (first 5):")
            for i, article in enumerate(paywalled_all[:5], 1):
                print(f"\n   {i}. PMID: {article.get('pmid', 'N/A')}")
                print(f"      Title: {article.get('title', 'No title')[:60]}...")
                print(f"      Journal: {article.get('journal', 'Unknown')}")
                print(f"      Access Type: {article.get('access_type', 'unknown')}")
                print(f"      Relevance Score: {article.get('relevance_score', 0)}")
        
        # Check for articles with missing access_type
        print("\n5. Checking for articles with missing/invalid access_type...")
        missing_access = [r for r in all_records if not r.get('access_type') or r.get('access_type') == 'unknown']
        print(f"   Articles with missing/unknown access_type: {len(missing_access)}")
        
        if missing_access:
            print("   Sample articles with missing access_type:")
            for i, article in enumerate(missing_access[:3], 1):
                print(f"   {i}. PMID: {article.get('pmid', 'N/A')}, Title: {article.get('title', 'No title')[:50]}")
        
        # Check relevance scores
        print("\n6. Relevance score distribution:")
        scores = [float(r.get('relevance_score', 0)) for r in all_records]
        if scores:
            print(f"   Min: {min(scores)}")
            print(f"   Max: {max(scores)}")
            print(f"   Avg: {sum(scores)/len(scores):.1f}")
            print(f"   Articles with score >= 70: {len([s for s in scores if s >= 70])}")
        
        # Check if articles have titles
        print("\n7. Checking article completeness...")
        with_title = [r for r in all_records if r.get('title') and r.get('title') != 'No title']
        with_journal = [r for r in all_records if r.get('journal') and r.get('journal') != 'Unknown Journal']
        print(f"   Articles with title: {len(with_title)}/{len(all_records)}")
        print(f"   Articles with journal: {len(with_journal)}/{len(all_records)}")
        
        print("\n" + "=" * 80)
        print("DIAGNOSIS COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during diagnosis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    diagnose()


