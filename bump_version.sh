#!/bin/bash
# Version Bump Script for Audio Transcription App
# Updates version across all project files

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo -e "${BLUE}Usage:${NC} $0 <new_version> [--no-backup]"
    echo ""
    echo "Examples:"
    echo "  $0 0.1.4"
    echo "  $0 0.2.0 --no-backup"
    echo ""
    echo "This script updates the version in:"
    echo "  - __version__.py"
    echo "  - pyproject.toml"
    echo "  - AudioTranscription.spec"
    echo ""
    exit 1
}

# Check if version argument is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Version number required${NC}"
    usage
fi

NEW_VERSION="$1"
NO_BACKUP=false

# Check for --no-backup flag
if [ "$2" = "--no-backup" ]; then
    NO_BACKUP=true
fi

# Validate version format (basic check for x.y.z)
if ! [[ "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}Error: Invalid version format. Use semantic versioning (e.g., 0.1.4)${NC}"
    exit 1
fi

# Get current version from __version__.py
if [ -f "__version__.py" ]; then
    CURRENT_VERSION=$(grep -oP "__version__ = \"\K[^\"]+(?=\")" __version__.py)
    echo -e "${BLUE}Current version:${NC} $CURRENT_VERSION"
else
    echo -e "${YELLOW}Warning: __version__.py not found${NC}"
    CURRENT_VERSION="unknown"
fi

echo -e "${BLUE}New version:${NC} $NEW_VERSION"
echo ""

# Confirm with user
read -p "Update version to $NEW_VERSION? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Aborted${NC}"
    exit 0
fi

# Create backups unless --no-backup is specified
if [ "$NO_BACKUP" = false ]; then
    echo -e "${BLUE}Creating backups...${NC}"
    [ -f "__version__.py" ] && cp __version__.py __version__.py.bak
    [ -f "pyproject.toml" ] && cp pyproject.toml pyproject.toml.bak
    [ -f "AudioTranscription.spec" ] && cp AudioTranscription.spec AudioTranscription.spec.bak
    echo -e "${GREEN}✓ Backups created (.bak files)${NC}"
fi

# Update __version__.py
if [ -f "__version__.py" ]; then
    echo -e "${BLUE}Updating __version__.py...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" __version__.py
    else
        # Linux
        sed -i "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" __version__.py
    fi
    echo -e "${GREEN}✓ Updated __version__.py${NC}"
else
    echo -e "${RED}✗ __version__.py not found${NC}"
fi

# Update pyproject.toml
if [ -f "pyproject.toml" ]; then
    echo -e "${BLUE}Updating pyproject.toml...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
    else
        # Linux
        sed -i "s/version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
    fi
    echo -e "${GREEN}✓ Updated pyproject.toml${NC}"
else
    echo -e "${RED}✗ pyproject.toml not found${NC}"
fi

# Update AudioTranscription.spec
if [ -f "AudioTranscription.spec" ]; then
    echo -e "${BLUE}Updating AudioTranscription.spec...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/'CFBundleVersion': '.*'/'CFBundleVersion': '$NEW_VERSION'/" AudioTranscription.spec
        sed -i '' "s/'CFBundleShortVersionString': '.*'/'CFBundleShortVersionString': '$NEW_VERSION'/" AudioTranscription.spec
    else
        # Linux
        sed -i "s/'CFBundleVersion': '.*'/'CFBundleVersion': '$NEW_VERSION'/" AudioTranscription.spec
        sed -i "s/'CFBundleShortVersionString': '.*'/'CFBundleShortVersionString': '$NEW_VERSION'/" AudioTranscription.spec
    fi
    echo -e "${GREEN}✓ Updated AudioTranscription.spec${NC}"
else
    echo -e "${RED}✗ AudioTranscription.spec not found${NC}"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}Version bump complete: $CURRENT_VERSION → $NEW_VERSION${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""

# Show what changed
echo -e "${BLUE}Changed files:${NC}"
git diff --stat __version__.py pyproject.toml AudioTranscription.spec 2>/dev/null || \
    echo "  (git not available, cannot show diff)"

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Update CHANGELOG.md with new version section"
echo "  2. Review changes: git diff"
echo "  3. Commit changes: git add . && git commit -m \"Bump version to $NEW_VERSION\""
echo "  4. Create tag: git tag v$NEW_VERSION"
echo "  5. Push: git push && git push --tags"
echo ""

if [ "$NO_BACKUP" = false ]; then
    echo -e "${YELLOW}Backup files created (.bak) - remove them when satisfied${NC}"
fi
