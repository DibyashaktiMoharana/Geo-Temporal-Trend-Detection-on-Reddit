# Geo-Temporal Trend Detection for Local Event Monitoring on Reddit

## Solution Architecture

<img width="2250" height="1609" alt="PJT-1 arch" src="https://github.com/user-attachments/assets/6e7fa1cd-5c02-4c9c-be17-289893926c93" />

## Project Structure

```
├── data/                    # Main Backend API (Reddit Scraper + Translation)
│   ├── app.py              # FastAPI application
│   ├── routes/             # API routes
│   │   ├── scrape_routes.py      # Reddit scraping endpoints
│   │   └── translation_routes.py # Translation endpoints
│   ├── controllers/        # Business logic
│   ├── database/           # Database connections
│   ├── models/             # Data models
│   └── requirements.txt
├── analysis-model/         # ML Analysis Model
│   ├── model.py
│   ├── api.py
│   └── requirements.txt
└── render.yaml            # Deployment configuration
```

## Quick Start - Main Backend (Reddit Scraper + Translation)

### Prerequisites
- Python 3.9+
- MongoDB Atlas account
- Reddit API credentials
- Sarvam AI API key

### Environment Setup

1. **Clone the repository**
```bash
git clone https://github.com/DibyashaktiMoharana/Geo-Temporal-Trend-Detection-on-Reddit.git
cd Geo-Temporal-Trend-Detection-on-Reddit
```

2. **Navigate to the data folder**
```bash
cd data
```

3. **Create and activate virtual environment**

**Windows (PowerShell):**
```bash
python -m venv env
.\env\Scripts\Activate.ps1
```

**Windows (CMD):**
```bash
python -m venv env
.\env\Scripts\activate.bat
```

**Linux/Mac:**
```bash
python -m venv env
source env/bin/activate
```

4. **Install dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

5. **Configure environment variables**

Create a `.env` file in the `data` folder with:
```env
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_app_name by u/your_username

MONGO_URI=your_mongodb_connection_string
SARVAM_API_KEY=your_sarvam_api_key
```

6. **Run the application**
```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at:
- **Main API**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

## API Endpoints

### Reddit Scraping
- `GET /api/scrape` - Scrape Reddit posts from a subreddit
  - Query params: `subreddit`, `method` (hot/new/top/rising), `time_filter`
- `GET /api/health` - Health check

### Translation (Sarvam AI)
- `POST /api/translation/translate` - Translate text from Indian languages to English
- `POST /api/translation/auto-translate` - Auto-detect language and translate
- `POST /api/translation/detect-language` - Detect language of input text
- `GET /api/translation/supported-languages` - List all supported languages
- `GET /api/translation/languages/major` - List major Indian languages
- `GET /api/translation/languages/additional` - List additional supported languages

## Running the Analysis Model

Navigate to the `analysis-model` directory and follow these steps:

```bash
cd analysis-model

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Run the model to generate data
python model.py

# Start the API server
python api.py
```

The Analysis Model API will be available at `http://localhost:5000`

## Deployment (Render)

This project is configured for deployment on Render using the `render.yaml` file.

### Prerequisites
1. Push your code to GitHub
2. Create a Render account
3. Connect your GitHub repository to Render

### Deploy Steps
1. In Render dashboard, click "New +" → "Blueprint"
2. Select your repository
3. Render will automatically detect `render.yaml`
4. Add environment variables in the Render dashboard:
   - `REDDIT_CLIENT_ID`
   - `REDDIT_CLIENT_SECRET`
   - `REDDIT_USER_AGENT`
   - `MONGO_URI`
   - `SARVAM_API_KEY`
5. Click "Apply" to deploy

### Build Commands (for manual setup)
```bash
cd data
pip install --no-cache-dir --upgrade pip
pip install --no-cache-dir -r requirements.txt
```

### Start Command
```bash
cd data
uvicorn app:app --host 0.0.0.0 --port $PORT
```

## Features

- **Reddit Scraping**: Fetch posts from any subreddit using various methods (hot, new, top, rising)
- **Multi-language Translation**: Translate 23+ Indian languages to English using Sarvam AI
- **Auto Language Detection**: Automatically detect and translate text
- **MongoDB Integration**: Store and manage scraped data
- **FastAPI**: Modern, fast API with automatic documentation
- **CORS Enabled**: Ready for frontend integration

## Contributing

Feel free to open issues or submit pull requests for improvements.

## License

This project is open source and available under the MIT License.
