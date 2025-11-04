#!/bin/bash
# Build script for Render deployment

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Downloading spaCy language model..."
python -m spacy download en_core_web_sm

# Check if data file exists, if not run model.py
if [ ! -f "cleaned_delhiData_with_labels.csv" ]; then
    echo "Data file not found. Running model.py to generate it..."
    
    # Check if source data exists
    if [ -f "delhiDatacsv.csv" ]; then
        echo "Running model.py..."
        python model.py
        echo "Model completed successfully!"
    else
        echo "WARNING: delhiDatacsv.csv not found. Skipping model generation."
        echo "API will start but data endpoints may not work."
    fi
else
    echo "Data file already exists. Skipping model generation."
fi

echo "Build completed!"
