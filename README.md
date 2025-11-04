# Geo-Temporal Trend Detection for Local Event Monitoring on Reddit

## Solution Architecture

<img width="2250" height="1609" alt="PJT-1 arch" src="https://github.com/user-attachments/assets/6e7fa1cd-5c02-4c9c-be17-289893926c93" />

## Running the Model

Navigate to the `analysis-model` directory and follow these steps:

```bash
# Install dependencies (if not done already)
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Run the model to generate data
python model.py

# Start the API server
python api.py
```

The API will be available at `http://localhost:5000`
