#!/bin/bash
# Test the complete HomeLab inventory database workflow

set -e  # Exit on error

echo "======================================================================"
echo "HomeLab Equipment Inventory Database - Complete Workflow Test"
echo "======================================================================"
echo

# Clean up any existing database for fresh test
if [ -f homelab_inventory.db ]; then
    echo "Removing existing database for fresh test..."
    rm homelab_inventory.db
fi

# Step 1: Import
echo "STEP 1: Importing from markdown..."
echo "----------------------------------------------------------------------"
python3 import_inventory.py
echo

# Step 2: Query tests
echo "STEP 2: Testing query commands..."
echo "----------------------------------------------------------------------"

echo "2a. Database statistics:"
python3 query_inventory.py stats
echo

echo "2b. SCPI-enabled equipment:"
python3 query_inventory.py scpi
echo

echo "2c. Network inventory:"
python3 query_inventory.py network
echo

echo "2d. Search for 'Rigol' equipment:"
python3 query_inventory.py search rigol
echo

echo "2e. List test equipment:"
python3 query_inventory.py list --category test_equipment
echo

echo "2f. Show details for equipment ID 19 (DMM-Keithley):"
python3 query_inventory.py show 19
echo

# Step 3: Export
echo "STEP 3: Exporting to markdown..."
echo "----------------------------------------------------------------------"
python3 export_markdown.py
echo

# Step 4: Verify export
echo "STEP 4: Verifying exported markdown..."
echo "----------------------------------------------------------------------"
if [ -f ../docs/hardware-inventory-auto.md ]; then
    lines=$(wc -l < ../docs/hardware-inventory-auto.md)
    echo "✓ Markdown file created: $lines lines"
    echo
    echo "First 10 lines:"
    head -10 ../docs/hardware-inventory-auto.md
else
    echo "ERROR: Markdown export file not found!"
    exit 1
fi

echo
echo "======================================================================"
echo "WORKFLOW TEST COMPLETE!"
echo "======================================================================"
echo
echo "Summary:"
echo "  ✓ Database created and populated from markdown"
echo "  ✓ Query tool working (stats, scpi, network, search, list, show)"
echo "  ✓ Markdown export generated successfully"
echo
echo "Database location: $(pwd)/homelab_inventory.db"
echo "Markdown export: $(pwd)/../docs/hardware-inventory-auto.md"
echo
echo "======================================================================"
