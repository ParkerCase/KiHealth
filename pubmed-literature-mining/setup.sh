#!/bin/bash
# Setup script for PubMed Literature Mining System

echo "Setting up PubMed Literature Mining System..."

# Create necessary directories
mkdir -p data/pdfs
mkdir -p logs
mkdir -p config

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cat > .env << EOF
# Xata Database Configuration
XATA_API_KEY=your_xata_api_key_here
XATA_DATABASE_URL=your_xata_database_url_here

# Unpaywall Configuration
UNPAYWALL_EMAIL=parker@stroomai.com

# PubMed API Configuration
PUBMED_EMAIL=parker@stroomai.com
PUBMED_TOOL=PubMedLiteratureMining

# Processing Configuration
MAX_ARTICLES_PER_RUN=100
RELEVANCE_THRESHOLD=70

# GitHub Configuration (optional, for issue creation)
GITHUB_REPO_OWNER=your_github_username
GITHUB_REPO_NAME=your_repo_name
GITHUB_TOKEN=your_github_token_here
EOF
    echo "Please edit .env file with your credentials"
else
    echo ".env file already exists"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Run tests
echo "Running tests..."
pytest tests/ -v

echo "Setup complete!"
echo "Next steps:"
echo "1. Edit .env file with your Xata credentials"
echo "2. Set up Xata database table (see README.md)"
echo "3. Configure GitHub secrets (see README.md)"
echo "4. Test locally: python scripts/pubmed_scraper.py"

