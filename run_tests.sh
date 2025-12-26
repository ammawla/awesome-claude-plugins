#!/bin/bash
#
# Test runner script for marketplace scraper
#

echo "Running Marketplace Scraper Tests"
echo "=================================="

# Check if pytest is available
if command -v pytest &> /dev/null; then
    echo "Using pytest..."
    python -m pytest tests/ -v --tb=short
else
    echo "pytest not found, installing..."
    pip install pytest
    python -m pytest tests/ -v --tb=short
fi

echo ""
echo "Test Summary:"
echo "- Unit tests: Configuration and validation logic"
echo "- Integration tests: Full workflow from config to README generation"
echo "- All tests validate the core functionality works correctly"