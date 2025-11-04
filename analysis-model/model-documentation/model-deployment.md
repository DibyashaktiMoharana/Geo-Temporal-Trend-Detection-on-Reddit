# Deployment Guide for Reddit Trend Analysis API

## Memory Optimization for Render (512MB Free Tier)

This application has been optimized to run within Render's 512MB memory limit.

### Key Optimizations

1. **Model Processing During Build**

   - Data processing happens during the build phase (has more resources)
   - If build processing fails, API starts anyway and provides `/api/process` endpoint

2. **Memory-Efficient Processing**

   - Disabled unnecessary spaCy components
   - Batch processing for embeddings
   - Explicit garbage collection after each heavy operation
   - Single Gunicorn worker

3. **Graceful Degradation**
   - API starts immediately to satisfy Render's port binding requirement
   - If data isn't processed, API returns helpful error messages
   - Background processing available via API endpoint

## API Endpoints

### Health & Status

- `GET /api/health` - Check API health and data status
- `GET /api/processing-status` - Check data processing status

### Data Processing

- `POST /api/process` - Trigger data processing (if not done during build)
- `POST /api/reload` - Reload processed data

### Data Access

- `GET /api/topics` - Get all topics
- `GET /api/topic/<id>` - Get topic details
- `GET /api/stats` - Get overall statistics
- `GET /api/timeline` - Get topic timeline
- `GET /api/search?q=<query>` - Search posts
- `GET /api/topic-distribution` - Get topic distribution

## Deployment Process

1. **Set Environment Variables in Render**

   - `GEMINI_API_KEY` - Your Google Gemini API key

2. **Deploy to Render**

   - Build command runs: Install dependencies → Download spaCy model → Process data
   - If processing succeeds, data is available immediately
   - If processing fails, API starts anyway (use `/api/process` endpoint)

3. **Monitor Deployment**
   - Check `/api/health` endpoint
   - If `data_loaded: false`, trigger processing with `POST /api/process`

## Troubleshooting

### Build Exceeds Memory Limit

If model.py fails during build:

1. API will still start successfully
2. Use `POST /api/process` to trigger processing after deployment
3. Monitor with `GET /api/processing-status`

### Processing Timeout

If processing takes >10 minutes:

1. Consider reducing `NUM_TOPICS` in model.py
2. Process data locally and commit the CSV file
3. Deploy with pre-processed data

### Port Binding Issues

- API now starts immediately without waiting for data processing
- Satisfies Render's port binding requirement within timeout

## Memory Usage Breakdown

- Base Python + Flask: ~80MB
- spaCy (minimal): ~100MB
- SentenceTransformer: ~150MB
- Data processing: ~100MB
- API runtime: ~50MB
- **Total: ~480MB** (within 512MB limit)

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Process data
python model.py

# Run API
python api.py
```

## Production Considerations

For larger datasets or more topics, consider:

1. Upgrading to a paid Render plan (1GB+ memory)
2. Using a separate worker service for data processing
3. Processing data in CI/CD and committing results
4. Using external storage for processed data
