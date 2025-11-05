# Reddit Geo-Temporal Trend Detection - Frontend

A modern React + TypeScript frontend for visualizing and analyzing Reddit trends with geo-temporal detection capabilities.

## Features

- 📊 **Interactive Dashboard** - Overview of all trends and statistics
- 🏷️ **Topic Exploration** - Browse and analyze detected topics
- 🔍 **Advanced Search** - Search posts with filters
- 📈 **Timeline Visualization** - View trends over time
- 🌐 **Reddit Scraper** - Scrape posts directly from Reddit
- 📱 **Responsive Design** - Works seamlessly on all devices

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **React Router** - Navigation
- **Recharts** - Data visualization
- **Tailwind CSS** - Styling
- **Axios** - API client
- **Lucide React** - Icons
- **React Hot Toast** - Notifications

## Prerequisites

- Node.js 18+ and npm/yarn
- Backend services running:
  - Analysis Model API (port 5000)
  - Data Scraper API (port 8000)

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── Layout.tsx   # Main layout with navigation
│   │   └── UI.tsx       # UI components (Card, Badge, etc.)
│   ├── pages/           # Page components
│   │   ├── Dashboard.tsx    # Main dashboard
│   │   ├── Topics.tsx       # Topics list
│   │   ├── TopicDetail.tsx  # Individual topic view
│   │   ├── Search.tsx       # Search interface
│   │   ├── Timeline.tsx     # Timeline visualization
│   │   └── Scraper.tsx      # Reddit scraper interface
│   ├── services/        # API services
│   │   └── api.ts       # API client
│   ├── types/           # TypeScript type definitions
│   │   └── index.ts     # Type definitions
│   ├── App.tsx          # Main app component
│   ├── main.tsx         # Entry point
│   └── index.css        # Global styles
├── public/              # Static assets
├── index.html           # HTML template
├── vite.config.ts       # Vite configuration
├── tailwind.config.js   # Tailwind CSS configuration
├── tsconfig.json        # TypeScript configuration
└── package.json         # Dependencies
```

## Configuration

### API Endpoints

The frontend is configured to proxy API requests to the backend services:

- `/api/*` → Analysis Model API (http://localhost:5000)
- `/scrape/api/*` → Data Scraper API (http://localhost:8000)

You can modify these in `vite.config.ts` if your backend runs on different ports.

## Key Features

### Dashboard
- Overview statistics (total posts, topics, comments, upvote ratio)
- Topic distribution pie chart
- Top 5 topics list
- Date range information

### Topics
- Browse all detected topics
- Sort by post count or topic ID
- Visual topic cards with statistics
- Quick navigation to topic details

### Topic Details
- Detailed statistics per topic
- Representative posts (most characteristic)
- Recent popular posts
- Links to original Reddit posts

### Search
- Full-text search across all posts
- Filter by topic
- Configurable result limit
- Rich post cards with metadata

### Timeline
- Visualize topic trends over time
- Toggle between daily, weekly, and monthly views
- Stacked bar chart showing top 5 topics
- Detailed breakdown by date

### Scraper
- Scrape posts from any subreddit
- Configure listing method (hot, new, top, rising)
- Set time filters
- Real-time scraping results

## API Integration

The frontend connects to two backend services:

1. **Analysis Model API** (Flask - Port 5000)
   - `/api/health` - Health check
   - `/api/topics` - Get all topics
   - `/api/topic/:id` - Get topic details
   - `/api/stats` - Get statistics
   - `/api/timeline` - Get timeline data
   - `/api/search` - Search posts

2. **Data Scraper API** (FastAPI - Port 8000)
   - `/scrape/api/scrape` - Scrape Reddit posts
   - `/scrape/api/health` - Health check

## Styling

The project uses Tailwind CSS with a custom color scheme:

- **Primary Color**: Blue (#3b82f6)
- **Success**: Green (#10b981)
- **Warning**: Amber (#f59e0b)
- **Error**: Red (#ef4444)

Customize colors in `tailwind.config.js`.

## Building for Production

1. Build the project:
```bash
npm run build
```

2. The production-ready files will be in the `dist/` directory.

3. Preview the production build:
```bash
npm run preview
```

## Deployment

### Option 1: Static Hosting (Netlify, Vercel, etc.)

1. Build the project: `npm run build`
2. Deploy the `dist/` directory
3. Configure environment variables for API endpoints if needed

### Option 2: Docker

Create a `Dockerfile` in the frontend directory:

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### API Connection Issues

If you see "Failed to load data" errors:

1. Ensure backend services are running
2. Check the API URLs in `vite.config.ts`
3. Verify CORS is enabled on backend services
4. Check browser console for detailed error messages

### Build Errors

If you encounter build errors:

1. Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
2. Clear Vite cache: `rm -rf .vite`
3. Check Node.js version: `node --version` (should be 18+)

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

This project is part of the Geo-Temporal Trend Detection system.

## Support

For issues or questions, please refer to the main project documentation.
