#!/usr/bin/env python3
"""
System Monitoring Script
Monitors the literature quality system and reports on status, improvements, and issues.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from literature_database import LiteratureDatabase
from probast_assessment import PROBASTAssessment


def monitor_system():
    """Monitor system status and improvements"""
    print("=" * 80)
    print("LITERATURE QUALITY SYSTEM MONITOR")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check database
    db_path = "data/literature.db"
    if not os.path.exists(db_path):
        print("⚠ Database not found. Run workflow to create it.")
        return
    
    db = LiteratureDatabase(db_path)
    stats = db.get_statistics()
    
    print("DATABASE STATISTICS")
    print("-" * 80)
    print(f"Total Articles: {stats.get('total_articles', 0):,}")
    print(f"Low Risk PROBAST: {stats.get('probast_low_risk', 0):,}")
    print(f"Moderate Risk: {stats.get('probast_moderate_risk', 0):,}")
    print(f"High Risk: {stats.get('probast_high_risk', 0):,}")
    print(f"Unclear Risk: {stats.get('probast_unclear', 0):,}")
    print(f"Used in Model: {stats.get('used_in_model', 0):,}")
    print()
    
    # Calculate quality metrics
    total = stats.get('total_articles', 0)
    low_risk = stats.get('probast_low_risk', 0)
    
    if total > 0:
        low_risk_pct = (low_risk / total) * 100
        print("QUALITY METRICS")
        print("-" * 80)
        print(f"Low Risk Percentage: {low_risk_pct:.1f}%")
        print(f"Articles Usable for Model: {low_risk:,} ({low_risk_pct:.1f}%)")
        print()
        
        # Access type breakdown
        access_types = stats.get('by_access_type', {})
        if access_types:
            print("ACCESS TYPE BREAKDOWN")
            print("-" * 80)
            for access_type, count in access_types.items():
                pct = (count / total) * 100
                print(f"{access_type.replace('_', ' ').title()}: {count:,} ({pct:.1f}%)")
            print()
    
    # Check for improvements
    print("SYSTEM IMPROVEMENTS")
    print("-" * 80)
    
    improvements = []
    
    # Check article count
    if total >= 100:
        improvements.append(f"✓ Large article database: {total:,} articles")
    elif total >= 10:
        improvements.append(f"✓ Growing database: {total:,} articles")
    else:
        improvements.append(f"⚠ Small database: {total:,} articles (run workflow to add more)")
    
    # Check Low Risk articles
    if low_risk >= 50:
        improvements.append(f"✓ Substantial Low Risk articles: {low_risk:,} usable for model")
    elif low_risk >= 10:
        improvements.append(f"✓ Good Low Risk coverage: {low_risk:,} usable for model")
    elif low_risk > 0:
        improvements.append(f"⚠ Limited Low Risk articles: {low_risk:,} (may need more screening)")
    else:
        improvements.append("⚠ No Low Risk articles yet (articles may need manual review)")
    
    # Check PROBAST distribution
    if total > 0:
        moderate = stats.get('probast_moderate_risk', 0)
        high = stats.get('probast_high_risk', 0)
        unclear = stats.get('probast_unclear', 0)
        
        if moderate + high + unclear > low_risk:
            improvements.append("⚠ More Moderate/High risk than Low risk - consider manual review")
        else:
            improvements.append("✓ Good PROBAST distribution")
    
    for improvement in improvements:
        print(improvement)
    
    print()
    print("=" * 80)
    print("SYSTEM STATUS: OPERATIONAL")
    print("=" * 80)
    
    # Recommendations
    print("\nRECOMMENDATIONS")
    print("-" * 80)
    
    if total < 100:
        print("1. Run workflow to fetch more articles:")
        print("   python scripts/literature_quality_workflow.py")
    
    if low_risk == 0 and total > 0:
        print("2. Review Moderate risk articles - some may be Low Risk with justification")
        print("3. Consider manual PROBAST assessment for high-value articles")
    
    if low_risk < 10:
        print("4. Continue running workflow to build Low Risk article database")
    
    print("\n5. For ASReview screening (optional):")
    print("   pip install asreview")
    print("   asreview web")
    print("   Upload: data/asreview_export.csv")


if __name__ == "__main__":
    monitor_system()
