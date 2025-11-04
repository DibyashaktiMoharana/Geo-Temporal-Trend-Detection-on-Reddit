# How Render Deployment Works - Complete Explanation

## Deployment Flow

### What Happens When You Deploy to Render:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. TRIGGER: You push code to GitHub                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. BUILD PHASE (Runs ONCE per deployment)                  │
│                                                             │
│    Command: pip install -r requirements.txt &&             │
│             python -m spacy download en_core_web_sm &&     │
│             python model.py (if added)                     │
│                                                             │
│    What happens:                                           │
│    • Installs all Python packages                          │
│    • Downloads spaCy language model                        │
│    • (Optional) Runs model.py to generate CSV              │
│                                                             │
│    Result: Environment is ready with all dependencies      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. START PHASE (Runs every time service restarts)          │
│                                                             │
│    Command: gunicorn api:app --bind 0.0.0.0:$PORT          │
│                                                             │
│    What happens:                                           │
│    • Starts Flask API server                               │
│    • Loads cleaned_delhiData_with_labels.csv               │
│    • Precomputes embeddings                                │
│    • Server listens on assigned port                       │
│                                                             │
│    Result: API is live and accessible                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. RUNNING: API accepts requests                           │
└─────────────────────────────────────────────────────────────┘
```

## Does model.py Run Automatically?

### **Current Setup: NO**

- By default, `model.py` does NOT run during deployment
- The API expects `cleaned_delhiData_with_labels.csv` to already exist

### **Why This Design?**

1. **Separation of Concerns**: Data processing vs. API serving
2. **Cost Control**: Avoid running expensive Gemini API calls on every deploy
3. **Speed**: Faster deployments without waiting for model to run
4. **Flexibility**: You control when to regenerate data

## Three Deployment Strategies

### **Strategy 1: Pre-Generate Locally** (Recommended for Free Tier)

**How it works:**

```powershell
# Step 1: Run model locally
python model.py

# Step 2: Commit the generated CSV
git add cleaned_delhiData_with_labels.csv delhiDatacsv.csv
git commit -m "Add data files"
git push

# Step 3: Deploy (just API, no model running)
# Render automatically deploys when you push
```

**Build Command in Render:**

```bash
pip install -r requirements.txt && python -m spacy download en_core_web_sm
```

**Pros:**

- Fast deployments
- No Gemini API costs during deployment
- Predictable behavior
- Works on free tier

**Cons:**

- Large files in git repository
- Manual data regeneration needed
- Data might become stale

---

### **Strategy 2: Generate During Build** (Updated Setup)

**How it works:**

```powershell
# Just push your code - model runs during build
git push
```

**Build Command in Render:**

```bash
pip install -r requirements.txt && python -m spacy download en_core_web_sm && python model.py
```

Or use the build script:

```bash
bash build.sh
```

**What happens:**

1. Render installs dependencies
2. Downloads spaCy model
3. **Runs model.py to generate CSV**
4. Starts API server

**Pros:**

- Automatic data generation
- Always fresh data
- No large files in git

**Cons:**

- Longer build time (10-15 minutes)
- Uses Gemini API credits on every deploy
- Requires source CSV in repository
- Might timeout on free tier

**Setup:**

```yaml
# render.yaml
buildCommand: pip install -r requirements.txt && python -m spacy download en_core_web_sm && python model.py
```

---

### **Strategy 3: Separate Data Processing** (Production)

**How it works:**

```
┌──────────────────┐         ┌──────────────────┐
│  Cron Job        │         │  Web Service     │
│  (runs model.py) │  ──────▶│  (serves API)    │
│  Daily/Weekly    │  Upload │  Reads CSV       │
└──────────────────┘         └──────────────────┘
         │
         ▼
   Cloud Storage
   (S3, GCS, etc)
```

**Components:**

1. **Web Service**: Just serves API (fast, cheap)
2. **Cron Job**: Runs model.py on schedule
3. **Storage**: Shared CSV file in cloud storage

**Pros:**

- Scalable and professional
- Fast deployments
- Scheduled data updates
- No timeout issues

**Cons:**

- More complex setup
- Requires paid Render plan for cron jobs
- Requires cloud storage setup

---

## Comparison Table

| Feature        | Strategy 1     | Strategy 2       | Strategy 3      |
| -------------- | -------------- | ---------------- | --------------- |
| Build Time     | Fast (2-3 min) | Slow (10-15 min) | Fast (2-3 min)  |
| Free Tier      | Works well     | Might timeout    | Needs paid plan |
| API Costs      | Only initial   | Every deploy     | Scheduled only  |
| Complexity     | Simple         | Simple           | Complex         |
| Data Freshness | Manual update  | Every deploy     | Scheduled       |
| Git Repo Size  | Large          | Small            | Small           |

## My Recommendation

### For Learning/Testing:

**Use Strategy 1** - Pre-generate locally

- Simple and reliable
- Works on free tier
- Full control

### For Small Projects:

**Use Strategy 2** - Generate during build

- Set up the build script I created
- Monitor build times
- Consider upgrading if timeouts occur

### For Production:

**Use Strategy 3** - Separate processing

- More robust and scalable
- Better cost control
- Professional architecture

## Quick Start Commands

### Strategy 1 (Recommended):

```powershell
# In analysis-model directory
python model.py
git add cleaned_delhiData_with_labels.csv delhiDatacsv.csv
git commit -m "Add generated data"
git push
```

**Render Build Command:**

```
pip install -r requirements.txt && python -m spacy download en_core_web_sm
```

### Strategy 2:

```powershell
# Just push - model runs automatically
git push
```

**Render Build Command:**

```
pip install -r requirements.txt && python -m spacy download en_core_web_sm && python run_model.py
```

## How to Check What's Running

### During Build:

- Go to Render Dashboard → Your Service → Logs
- Watch the build logs in real-time
- You'll see if model.py is running

### After Deployment:

```bash
# Check API health
curl https://your-app.onrender.com/api/health

# Should return:
{
  "status": "healthy",
  "data_loaded": true,
  "embeddings_loaded": true
}
```

## Common Issues

### Issue: "Data not loaded" after deployment

**Cause**: CSV file not available  
**Solution**: Use Strategy 1 and commit the CSV file

### Issue: Build timeout

**Cause**: model.py takes too long on free tier  
**Solution**: Use Strategy 1 or upgrade to paid tier

### Issue: Out of memory

**Cause**: Free tier has 512MB RAM limit  
**Solution**: Reduce NUM_TOPICS or upgrade plan

## Understanding the Files

```
analysis-model/
├── model.py           # Original model (keep for reference)
├── run_model.py       # Improved version with better error handling
├── api.py             # Flask API server (THIS runs on Render)
├── build.sh           # Optional build script
├── requirements.txt   # Python dependencies
├── Procfile          # Tells Render how to start app
└── render.yaml       # Infrastructure as code
```

**What runs where:**

- **Locally**: `model.py` or `run_model.py` to generate data
- **On Render Build**: Dependencies installation (+ optionally model.py)
- **On Render Runtime**: `api.py` (Flask server)

## Next Steps

1. Choose your strategy (I recommend Strategy 1 for now)
2. Follow the Quick Start Commands
3. Deploy to Render
4. Test your API endpoints
5. Monitor logs for any issues

Need help? Check `DEPLOYMENT.md` for detailed Render setup instructions!
