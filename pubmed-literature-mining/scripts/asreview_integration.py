#!/usr/bin/env python3
"""
ASReview LAB Integration
AI-powered screening tool for literature review.

ASReview LAB is free, open-source, and runs locally.
No data sent anywhere - complete privacy.
"""

import os
import sys
import json
import logging
import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ASReviewIntegration:
    """Integration with ASReview LAB for AI-powered screening"""
    
    def __init__(self, project_path: str = "data/asreview_projects"):
        """
        Initialize ASReview integration
        
        Args:
            project_path: Path to store ASReview projects
        """
        self.project_path = project_path
        os.makedirs(project_path, exist_ok=True)
        
        # Check if ASReview is installed
        try:
            import asreview
            self.asreview_available = True
            logger.info("ASReview LAB is available")
        except ImportError:
            self.asreview_available = False
            logger.warning("ASReview LAB not installed. Install with: pip install asreview")
    
    def create_project(self, articles: List[Dict], project_name: str = "doc_literature") -> Optional[str]:
        """
        Create ASReview project from articles
        
        Args:
            articles: List of article dictionaries
            project_name: Name for the ASReview project
            
        Returns:
            Path to ASReview project file, or None if failed
        """
        if not self.asreview_available:
            logger.error("ASReview LAB not available")
            return None
        
        try:
            import asreview
            from asreview import ASReviewProject
            
            # Create project
            project_path = os.path.join(self.project_path, project_name)
            project = ASReviewProject.create(project_path)
            
            # Convert articles to DataFrame
            df = self._articles_to_dataframe(articles)
            
            # Add data to project
            project.add_data(df)
            
            logger.info(f"ASReview project created at {project_path}")
            return project_path
            
        except Exception as e:
            logger.error(f"Error creating ASReview project: {e}")
            return None
    
    def export_for_asreview(self, articles: List[Dict], output_path: str = "data/asreview_export.csv") -> bool:
        """
        Export articles to CSV format for ASReview LAB
        
        Args:
            articles: List of article dictionaries
            output_path: Path to output CSV file
            
        Returns:
            True if successful
        """
        try:
            df = self._articles_to_dataframe(articles)
            df.to_csv(output_path, index=False)
            logger.info(f"Exported {len(articles)} articles to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting articles for ASReview: {e}")
            return False
    
    def import_screening_results(self, project_path: str) -> Optional[List[Dict]]:
        """
        Import screening results from ASReview project
        
        Args:
            project_path: Path to ASReview project
            
        Returns:
            List of articles with screening results, or None if failed
        """
        if not self.asreview_available:
            logger.error("ASReview LAB not available")
            return None
        
        try:
            import asreview
            from asreview import ASReviewProject
            
            project = ASReviewProject(project_path)
            
            # Get labeled data (screened articles)
            labeled = project.get_labeled()
            
            # Convert to list of dictionaries
            results = []
            for idx, row in labeled.iterrows():
                results.append({
                    "pmid": str(row.get("pmid", "")),
                    "title": row.get("title", ""),
                    "abstract": row.get("abstract", ""),
                    "asreview_relevant": bool(row.get("label", 0) == 1),
                    "asreview_screened": True
                })
            
            logger.info(f"Imported {len(results)} screening results from ASReview")
            return results
            
        except Exception as e:
            logger.error(f"Error importing ASReview results: {e}")
            return None
    
    def _articles_to_dataframe(self, articles: List[Dict]) -> pd.DataFrame:
        """Convert articles list to DataFrame for ASReview"""
        records = []
        
        for article in articles:
            record = {
                "pmid": article.get("pmid", ""),
                "title": article.get("title", ""),
                "abstract": article.get("abstract", ""),
                "authors": article.get("authors", ""),
                "journal": article.get("journal", ""),
                "doi": article.get("doi", ""),
                "publication_date": article.get("publication_date", ""),
            }
            records.append(record)
        
        df = pd.DataFrame(records)
        return df
    
    def get_screening_instructions(self) -> str:
        """Get instructions for using ASReview LAB"""
        return """
# ASReview LAB Screening Instructions

## Installation
```bash
pip install asreview
```

## Usage

1. **Export articles for screening:**
   ```python
   from scripts.asreview_integration import ASReviewIntegration
   
   asreview = ASReviewIntegration()
   asreview.export_for_asreview(articles, "data/articles_for_screening.csv")
   ```

2. **Open ASReview LAB:**
   ```bash
   asreview web
   ```

3. **Create new project:**
   - Click "New Project"
   - Upload `data/articles_for_screening.csv`
   - Select "Title" and "Abstract" as text fields
   - Select "pmid" as identifier

4. **Start screening:**
   - ASReview will use AI to prioritize articles
   - Review and label: Relevant (1) or Irrelevant (0)
   - AI learns from your decisions and improves prioritization

5. **Export results:**
   - After screening, export results
   - Import back into system using `import_screening_results()`

## Benefits

- **AI-powered prioritization**: Most relevant articles shown first
- **Active learning**: System learns from your decisions
- **Time-saving**: Screen 1000s of articles efficiently
- **Free and open-source**: No subscriptions, no data sent anywhere
- **Local processing**: Complete privacy

## Tips

- Start with 50-100 manual labels for best AI performance
- Review at least 10% of articles for quality control
- Use "Prioritize" mode for faster screening
- Export results regularly to avoid data loss
"""


if __name__ == "__main__":
    # Test ASReview integration
    asreview = ASReviewIntegration()
    
    test_articles = [
        {
            "pmid": "12345678",
            "title": "Test Article 1",
            "abstract": "This is a test abstract about knee osteoarthritis.",
            "authors": "Smith J, Doe A",
            "journal": "Test Journal",
            "doi": "10.1234/test",
            "publication_date": "2023-01-01"
        },
        {
            "pmid": "12345679",
            "title": "Test Article 2",
            "abstract": "Another test abstract about total knee replacement.",
            "authors": "Johnson B, Williams C",
            "journal": "Another Journal",
            "doi": "10.1234/test2",
            "publication_date": "2023-02-01"
        }
    ]
    
    # Export for ASReview
    success = asreview.export_for_asreview(test_articles, "test_asreview_export.csv")
    print(f"Export successful: {success}")
    
    # Print instructions
    print(asreview.get_screening_instructions())
    
    # Cleanup
    if os.path.exists("test_asreview_export.csv"):
        os.remove("test_asreview_export.csv")
