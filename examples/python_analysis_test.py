#!/usr/bin/env python3
"""
Test script for Python analysis pipeline.
This script verifies:
1. Fetching a Python repository (e.g. django/django or flask/flask)
2. Creating a CodeQL database
3. Running Python-specific queries
4. Processing results with LLM
"""

import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.codeql.fetch_repos import fetch_codeql_dbs
from src.codeql.run_codeql_queries import compile_and_run_codeql_queries as run_codeql_queries
from src.vulnhalla import IssueAnalyzer
from src.utils.logger import setup_logging, get_logger

logger = get_logger(__name__)

def main():
    setup_logging()

    # Configuration
    REPO = "pallets/flask"  # A well-known Python repo
    LANG = "python"

    logger.info(f"Starting Python analysis test for {REPO}...")

    # Step 1: Fetch/Create Database
    logger.info("Step 1: Fetching/Creating CodeQL Database...")
    fetch_codeql_dbs(
        lang=LANG,
        max_repos=1,
        threads=4,
        single_repo=REPO
    )

    # Step 2: Run Queries
    logger.info("Step 2: Running CodeQL Queries...")
    db_path = os.path.join("output/databases", LANG, REPO.split("/")[1])
    if not os.path.exists(db_path):
        logger.error(f"Database not found at {db_path}")
        return

    run_codeql_queries(
        lang=LANG
    )

    # Step 3: LLM Analysis
    logger.info("Step 3: Running LLM Analysis...")
    analyzer = IssueAnalyzer(lang=LANG)

    # Note: We just run the analysis part, assuming config is loaded from .env
    analyzer.run()

    logger.info("Test complete! Check output/results/python for results.")

if __name__ == "__main__":
    main()
