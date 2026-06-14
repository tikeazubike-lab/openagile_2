#!/bin/bash

# Fix Registrar Total Market Value Query
# Updates the aggregation query in all registrar files

set -e

REGISTRARS_DIR="../Registrars"

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

echo "Fixing registrar total market value queries..."
echo ""

cd "$REGISTRARS_DIR"

count=0
for file in *.md; do
    if [ -f "$file" ]; then
        # Replace the faulty aggregation query
        # Old: sum(rows.shares_held * rows.latest_price)
        # New: sum(shares_held * latest_price)
        sed -i 's/sum(rows\.shares_held \* rows\.latest_price)/sum(shares_held * latest_price)/g' "$file"
        
        # Also ensure it's properly formatted with rounding
        sed -i 's/sum(rows\.value)/sum(shares_held * latest_price)/g' "$file"
        
        echo -e "${GREEN}✓${NC} Updated: $file"
        count=$((count + 1))
    fi
done

echo ""
echo -e "${GREEN}Successfully updated $count registrar files${NC}"
