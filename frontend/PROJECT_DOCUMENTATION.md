# Reddit Geo-Temporal Trend Detection - Complete Project Documentation

## Project Overview

This project provides a complete solution for detecting and analyzing geo-temporal trends in Reddit posts. It consists of three main components:

1. **Frontend (React + TypeScript)** - Modern web interface
2. **Analysis Model API (Flask)** - ML-based trend detection
3. **Data Scraper API (FastAPI)** - Reddit data collection

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│                   (React + TypeScript)                       │
│                    Port: 3000                                │
└─────────────┬───────────────────────────┬───────────────────┘
              │                           │
              │ HTTP/REST                 │ HTTP/REST
              │                           │
    ┌─────────▼─────────┐       ┌────────▼──────────┐
    │  Analysis Model   │       │  Data Scraper     │
    │  API (Flask)      │       │  API (FastAPI)    │
    │  Port: 5000       │       │  Port: 8000       │
    └─────────┬─────────┘       └────────┬──────────┘
              │                           │
              │                           │
        ┌─────▼─────┐               ┌────▼─────┐
        │  CSV/JSON │               │ MongoDB  │
        │  Storage  │               │ Database │
        └───────────┘               └──────────┘
```

## Directory Structure

```
Geo-Temporal-Trend-Detection-on-Reddit/
├── frontend/                    # React frontend application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API integration
│   │   └── types/              # TypeScript definitions
│   ├── package.json
│   ├── vite.config.ts
│   ├── README.md
│   └── SETUP.md
│
├── analysis-model/             # ML-based analysis service
│   ├── api.py                  # Flask API
│   ├── model.py                # ML model
│   ├── requirements.txt
│   └── model-documentation/
│
├── data/                       # Data scraper service
│   ├── app.py                  # FastAPI application
│   ├── controllers/
│   ├── routes/
│   ├── models/
│   └── requirements.txt
│
├── sarvam/                     # Translation service
│   ├── app.py
│   └── requirements.txt
│
└── documentation/              # Project documentation
    ├── api-documentation.md
    ├── deploy.md
    ├── model.md
    └── setup_venv.md
```

## Getting Started

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.8+
- **MongoDB** (for data scraper)
- **Git**

### Installation Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/DibyashaktiMoharana/Geo-Temporal-Trend-Detection-on-Reddit.git
cd Geo-Temporal-Trend-Detection-on-Reddit
```

#### 2. Setup Backend Services

**Analysis Model API:**
```bash
cd analysis-model
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python model.py  # Generate initial data
python api.py    # Starts on port 5000
```

**Data Scraper API:**
```bash
cd data
pip install -r requirements.txt
# Configure MongoDB connection in database/connectdb.py
python app.py    # Starts on port 8000
```

#### 3. Setup Frontend

**Windows:**
```bash
cd frontend
start.bat
```

**Linux/Mac:**
```bash
cd frontend
chmod +x start.sh
./start.sh
```

**Or manually:**
```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Features

### Frontend Features

#### 1. Dashboard
- Overview statistics (posts, topics, comments)
- Topic distribution pie chart
- Top 5 trending topics
- Date range visualization

#### 2. Topics Browser
- List all detected topics
- Sort by post count or ID
- Visual topic cards
- Direct navigation to details

#### 3. Topic Details
- Comprehensive topic statistics
- Representative posts (ML-selected)
- Recent popular posts
- Links to original Reddit posts

#### 4. Search
- Full-text search across posts
- Filter by topic
- Configurable result limits
- Rich result cards with metadata

#### 5. Timeline
- Visualize trends over time
- Daily/Weekly/Monthly intervals
- Interactive charts
- Detailed breakdowns

#### 6. Reddit Scraper
- Scrape any subreddit
- Multiple listing methods (hot, new, top, rising)
- Time filters
- Real-time progress

### Backend Features

#### Analysis Model API (Flask)
- Topic detection using ML clustering
- Automatic topic labeling with Gemini AI
- Representative post selection
- Multilingual support
- Timeline analysis
- Search functionality

#### Data Scraper API (FastAPI)
- Reddit post scraping
- Multiple subreddit support
- Various listing methods
- MongoDB storage
- Automatic data cleaning

## API Endpoints

### Analysis Model API (Port 5000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/topics` | GET | Get all topics |
| `/api/topic/<id>` | GET | Get topic details |
| `/api/stats` | GET | Get statistics |
| `/api/timeline` | GET | Get timeline data |
| `/api/search` | GET | Search posts |
| `/api/topic-distribution` | GET | Get topic distribution |
| `/api/process` | POST | Trigger data processing |

### Data Scraper API (Port 8000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/scrape/api/scrape` | GET | Scrape Reddit posts |
| `/scrape/api/health` | GET | Health check |

## Technology Stack

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router** - Routing
- **Recharts** - Visualizations
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Lucide React** - Icons
- **React Hot Toast** - Notifications

### Backend
- **Flask** - Analysis API framework
- **FastAPI** - Scraper API framework
- **scikit-learn** - ML clustering
- **spaCy** - NLP processing
- **Google Gemini** - AI labeling
- **MongoDB** - Data storage
- **pandas** - Data processing

## Configuration

### Frontend Configuration

Create `frontend/.env`:
```env
VITE_API_BASE_URL=http://localhost:5000
VITE_SCRAPER_API_BASE_URL=http://localhost:8000
```

### Backend Configuration

**Analysis Model** - `analysis-model/.env`:
```env
GEMINI_API_KEY=your_api_key_here
LABELED_DATA_PATH=cleaned_delhiData_with_labels.csv
```

**Data Scraper** - Configure MongoDB in `data/database/connectdb.py`

## Development Workflow

### Running Development Environment

1. **Terminal 1** - Analysis Model:
```bash
cd analysis-model
python api.py
```

2. **Terminal 2** - Data Scraper:
```bash
cd data
python app.py
```

3. **Terminal 3** - Frontend:
```bash
cd frontend
npm run dev
```

### Making Changes

**Frontend:**
1. Edit files in `frontend/src/`
2. Changes will hot-reload automatically
3. Build for production: `npm run build`

**Backend:**
1. Edit Python files
2. Restart the server
3. Test with the frontend

## Deployment

### Frontend Deployment

**Option 1: Netlify/Vercel**
```bash
cd frontend
npm run build
# Deploy the dist/ folder
```

**Option 2: Docker**
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

### Backend Deployment

See `documentation/deploy.md` for detailed deployment instructions.

## Troubleshooting

### Common Issues

1. **Frontend can't connect to backend**
   - Ensure backend services are running
   - Check port numbers (5000, 8000)
   - Verify CORS is enabled

2. **TypeScript errors in frontend**
   - Run: `npm install`
   - Clear cache: `rm -rf node_modules/.vite`

3. **Python import errors**
   - Activate virtual environment
   - Run: `pip install -r requirements.txt`

4. **MongoDB connection failed**
   - Check MongoDB is running
   - Verify connection string in `connectdb.py`

## Testing

### Frontend Testing
```bash
cd frontend
npm run lint      # Check code quality
npm run build     # Test production build
```

### API Testing
```bash
# Test Analysis API
curl http://localhost:5000/api/health

# Test Scraper API
curl http://localhost:8000/scrape/api/health
```

## Performance Optimization

### Frontend
- Code splitting with React.lazy()
- Image optimization
- Memoization for expensive computations
- Virtual scrolling for large lists

### Backend
- Caching with Redis
- Database indexing
- Batch processing
- Async operations

## Security Considerations

1. **API Keys**: Store in environment variables
2. **CORS**: Configure allowed origins
3. **Rate Limiting**: Implement on API endpoints
4. **Input Validation**: Sanitize all user inputs
5. **Authentication**: Add if needed for production

## Contributing

1. Create a feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## License

[Your License Here]

## Support

For issues and questions:
- Check documentation files
- Review API documentation
- Check browser console for errors
- Verify all services are running

## Roadmap

- [ ] User authentication
- [ ] Real-time updates with WebSockets
- [ ] Export functionality (PDF, CSV)
- [ ] Advanced filtering options
- [ ] Mobile app
- [ ] API rate limiting
- [ ] Caching layer
- [ ] Unit and integration tests

## Acknowledgments

- Reddit API
- Google Gemini AI
- spaCy NLP library
- React community
- Open source contributors

---

**Version:** 1.0.0  
**Last Updated:** November 5, 2025  
**Repository:** https://github.com/DibyashaktiMoharana/Geo-Temporal-Trend-Detection-on-Reddit
