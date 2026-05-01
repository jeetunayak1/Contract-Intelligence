#!/bin/bash

# Setup Git Hooks and Secret Detection
# This script installs pre-commit hooks to prevent secrets from being committed

set -e

echo "🔒 Setting up Git hooks and secret detection..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed"
    exit 1
fi

# Install pre-commit
echo "📦 Installing pre-commit..."
pip3 install pre-commit detect-secrets

# Install git hooks
echo "🔧 Installing git hooks..."
pre-commit install

# Run detect-secrets scan to create baseline
echo "🔍 Scanning for existing secrets..."
detect-secrets scan --baseline .secrets.baseline

echo ""
echo -e "${GREEN}✅ Git hooks installed successfully!${NC}"
echo ""
echo "What happens now:"
echo "  • Every commit will be scanned for secrets"
echo "  • Large files (>1MB) will be blocked"
echo "  • Private keys will be detected"
echo "  • Code will be formatted automatically"
echo ""
echo "To bypass hooks (not recommended):"
echo "  git commit --no-verify"
echo ""
echo "To manually run checks:"
echo "  pre-commit run --all-files"
echo ""

# Made with Bob
