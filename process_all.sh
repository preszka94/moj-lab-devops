#!/bin/bash

# Define the directory where incoming invoices are stored
INVOICE_DIR="input_invoices"

echo "🚀 Starting batch processing for directory: $INVOICE_DIR"
echo "--------------------------------------------------------"

# For Loop - Iterate through every file in the directory
for file in "$INVOICE_DIR"/*; do
    
    # Security check: Ensure the item is actually a file (not a sub-folder)
    if [ -f "$file" ]; then
        echo "⏳ Handing off to Python backend: $file"
        
        # Execute the Python backend app and pass the file path as an argument
        python3 scripts/backend_app.py "$file"
    fi
    
done

echo "========================================================"
echo "✅ All documents in the queue have been processed."
