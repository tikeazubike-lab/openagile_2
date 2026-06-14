#!/bin/bash

# ============================================
# OpenAgile Board - Directory Issue Diagnostic
# ============================================
# This script helps diagnose why directories
# were not created properly
# ============================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "   OpenAgile Board - Directory Diagnostic Tool"
echo "═══════════════════════════════════════════════════════════"
echo ""

OPENAGILE_DIR="${HOME}/openagile"

# Check 1: Does openagile directory exist?
echo -e "${BLUE}[CHECK 1]${NC} Checking if openagile directory exists..."
if [ -d "$OPENAGILE_DIR" ]; then
    echo -e "${GREEN}✓${NC} Directory exists: $OPENAGILE_DIR"
    echo "  Owner: $(stat -c '%U:%G' "$OPENAGILE_DIR" 2>/dev/null || stat -f '%Su:%Sg' "$OPENAGILE_DIR" 2>/dev/null)"
    echo "  Permissions: $(stat -c '%a' "$OPENAGILE_DIR" 2>/dev/null || stat -f '%A' "$OPENAGILE_DIR" 2>/dev/null)"
else
    echo -e "${RED}✗${NC} Directory does not exist: $OPENAGILE_DIR"
    echo ""
    echo "Solution: Create it with:"
    echo "  mkdir -p $OPENAGILE_DIR"
    exit 1
fi

# Check 2: Can we write to it?
echo ""
echo -e "${BLUE}[CHECK 2]${NC} Checking write permissions..."
if [ -w "$OPENAGILE_DIR" ]; then
    echo -e "${GREEN}✓${NC} Directory is writable"
else
    echo -e "${RED}✗${NC} Directory is NOT writable"
    echo ""
    echo "Solution: Fix permissions with:"
    echo "  sudo chown -R \$USER:\$USER $OPENAGILE_DIR"
    echo "  chmod -R 755 $OPENAGILE_DIR"
    exit 1
fi

# Check 3: What's currently in it?
echo ""
echo -e "${BLUE}[CHECK 3]${NC} Current directory structure..."
cd "$OPENAGILE_DIR" || exit 1
echo "Working directory: $(pwd)"
echo ""

if command -v tree &> /dev/null; then
    tree -L 3 -a
else
    echo "Contents:"
    ls -lah
    echo ""
    echo "Subdirectories:"
    find . -type d -maxdepth 3 | sort
fi

# Check 4: Test directory creation
echo ""
echo -e "${BLUE}[CHECK 4]${NC} Testing directory creation..."

TEST_DIR="test_dir_$(date +%s)"
echo "Attempting to create test directory: $TEST_DIR"

if mkdir -p "$TEST_DIR/subdir/deepdir" 2>/dev/null; then
    if [ -d "$TEST_DIR/subdir/deepdir" ]; then
        echo -e "${GREEN}✓${NC} Successfully created nested test directories"
        rm -rf "$TEST_DIR"
        echo -e "${GREEN}✓${NC} Successfully removed test directories"
    else
        echo -e "${RED}✗${NC} mkdir succeeded but directory doesn't exist!"
        echo "This is unusual. Check filesystem."
    fi
else
    echo -e "${RED}✗${NC} Failed to create test directory"
    echo "Error: $?"
fi

# Check 5: Expected directories
echo ""
echo -e "${BLUE}[CHECK 5]${NC} Checking for expected OpenAgile directories..."

EXPECTED_DIRS=(
    "configs"
    "configs/traefik"
    "configs/prometheus"
    "configs/grafana"
    "configs/grafana/provisioning"
    "configs/grafana/provisioning/datasources"
    "configs/grafana/provisioning/dashboards"
    "configs/grafana/dashboards"
    "configs/n8n"
    "configs/gitea"
    "configs/woodpecker"
    "scripts"
    "backups"
    "monitoring"
    "erpnext"
    "erpnext/sites"
    "pipelines"
    "pipelines/examples"
)

FOUND=0
MISSING=0

for dir in "${EXPECTED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $dir"
        ((FOUND++))
    else
        echo -e "${RED}✗${NC} $dir (missing)"
        ((MISSING++))
    fi
done

echo ""
echo "Summary: $FOUND found, $MISSING missing"

# Check 6: Disk space
echo ""
echo -e "${BLUE}[CHECK 6]${NC} Checking disk space..."
df -h "$OPENAGILE_DIR"

AVAILABLE=$(df -BG "$OPENAGILE_DIR" | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$AVAILABLE" -lt 10 ]; then
    echo -e "${RED}⚠${NC} Low disk space: ${AVAILABLE}GB available"
else
    echo -e "${GREEN}✓${NC} Sufficient disk space: ${AVAILABLE}GB available"
fi

# Check 7: System limits
echo ""
echo -e "${BLUE}[CHECK 7]${NC} Checking system limits..."
echo "Max open files: $(ulimit -n)"
echo "Max user processes: $(ulimit -u)"

# Check 8: Current user info
echo ""
echo -e "${BLUE}[CHECK 8]${NC} Current user information..."
echo "User: $(whoami)"
echo "UID: $(id -u)"
echo "GID: $(id -g)"
echo "Groups: $(groups)"
echo "Home: $HOME"

# Generate report
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "                    DIAGNOSTIC SUMMARY"
echo "═══════════════════════════════════════════════════════════"
echo ""

if [ $MISSING -eq 0 ]; then
    echo -e "${GREEN}✓ ALL CHECKS PASSED${NC}"
    echo ""
    echo "All expected directories are present."
    echo "If you're still having issues, check:"
    echo "  1. Script execution location"
    echo "  2. Script syntax/errors in deploy script"
    echo "  3. Whether script actually ran to completion"
else
    echo -e "${YELLOW}⚠ MISSING DIRECTORIES DETECTED${NC}"
    echo ""
    echo "Fix this by running:"
    echo "  cd $OPENAGILE_DIR"
    echo "  ./setup-directories.sh"
    echo ""
    echo "Or manually create directories:"
    echo "  cd $OPENAGILE_DIR"
    for dir in "${EXPECTED_DIRS[@]}"; do
        if [ ! -d "$dir" ]; then
            echo "  mkdir -p $dir"
        fi
    done
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""

# Quick fix option
if [ $MISSING -gt 0 ]; then
    read -p "Create missing directories now? (yes/no): " create_now
    if [ "$create_now" = "yes" ]; then
        echo ""
        echo "Creating missing directories..."
        for dir in "${EXPECTED_DIRS[@]}"; do
            if [ ! -d "$dir" ]; then
                if mkdir -p "$dir" 2>/dev/null; then
                    echo -e "${GREEN}✓${NC} Created: $dir"
                else
                    echo -e "${RED}✗${NC} Failed: $dir"
                fi
            fi
        done
        echo ""
        echo "Done! Verify with:"
        echo "  cd $OPENAGILE_DIR && ls -la"
    fi
fi

echo ""
