# Frontend Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The application will open at `http://localhost:3000`

## Full Setup Instructions

### Prerequisites

Ensure you have the following installed:
- Node.js 18 or higher
- npm or yarn
- Git

Check your Node.js version:
```bash
node --version
```

### Step 1: Install Dependencies

Navigate to the frontend directory and install all required packages:

```bash
cd frontend
npm install
```

This will install:
- React 18
- TypeScript
- Vite
- React Router
- Recharts (for visualizations)
- Tailwind CSS
- Axios
- And other dependencies

### Step 2: Configure Environment (Optional)

If you need to customize API endpoints:

1. Copy the example environment file:
```bash
copy .env.example .env
```

2. Edit `.env` and update the API URLs if your backend runs on different ports:
```
VITE_API_BASE_URL=http://localhost:5000
VITE_SCRAPER_API_BASE_URL=http://localhost:8000
```

### Step 3: Start Backend Services

Before running the frontend, ensure both backend services are running:

**Terminal 1 - Analysis Model API:**
```bash
cd analysis-model
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python model.py  # Generate initial data
python api.py    # Start API on port 5000
```

**Terminal 2 - Data Scraper API:**
```bash
cd data
pip install -r requirements.txt
python app.py    # Start API on port 8000
```

### Step 4: Start Frontend

In a new terminal:

```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:3000` and automatically proxy API requests to the backend services.

### Step 5: Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

You should see the dashboard with navigation to:
- Dashboard
- Topics
- Search
- Timeline
- Scraper

## Development Workflow

### Running Development Server

```bash
npm run dev
```

Features:
- Hot Module Replacement (HMR)
- Fast refresh
- TypeScript type checking
- Automatic browser reload

### Building for Production

```bash
npm run build
```

This creates an optimized production build in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

Preview the production build locally before deployment.

### Linting

```bash
npm run lint
```

Check for code quality issues and TypeScript errors.

## Project Structure Explanation

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Layout.tsx      # Main layout wrapper with sidebar
│   │   └── UI.tsx          # Reusable UI elements
│   │
│   ├── pages/              # Page components (routes)
│   │   ├── Dashboard.tsx   # Main dashboard with stats
│   │   ├── Topics.tsx      # List all topics
│   │   ├── TopicDetail.tsx # Individual topic details
│   │   ├── Search.tsx      # Search interface
│   │   ├── Timeline.tsx    # Timeline visualization
│   │   └── Scraper.tsx     # Reddit scraper interface
│   │
│   ├── services/           # API integration
│   │   └── api.ts          # Axios API client
│   │
│   ├── types/              # TypeScript definitions
│   │   └── index.ts        # Type definitions
│   │
│   ├── App.tsx             # Main app with routing
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles + Tailwind
│
├── public/                 # Static assets
├── index.html              # HTML template
├── vite.config.ts          # Vite configuration
├── tailwind.config.js      # Tailwind CSS config
├── tsconfig.json           # TypeScript config
└── package.json            # Dependencies
```

## Common Issues & Solutions

### Issue: "Cannot find module" errors

**Solution:**
```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: API connection failed

**Solutions:**
1. Check if backend services are running:
   - Analysis API: `http://localhost:5000/api/health`
   - Scraper API: `http://localhost:8000/scrape/api/health`

2. Verify proxy configuration in `vite.config.ts`

3. Check browser console for CORS errors

### Issue: Port 3000 already in use

**Solution:**
Kill the process using port 3000 or change the port in `vite.config.ts`:
```ts
server: {
  port: 3001, // Change to any available port
}
```

### Issue: Build errors

**Solution:**
```bash
# Clear Vite cache
rm -rf node_modules/.vite

# Reinstall dependencies
npm install

# Try building again
npm run build
```

### Issue: TypeScript errors

**Solution:**
1. Check your Node.js version (should be 18+)
2. Delete node_modules and reinstall
3. Check `tsconfig.json` configuration

## IDE Setup

### VS Code (Recommended)

Install recommended extensions:
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- TypeScript

VS Code will automatically suggest these when you open the project.

### Settings

Create `.vscode/settings.json`:
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

## Customization

### Changing Colors

Edit `tailwind.config.js`:
```js
theme: {
  extend: {
    colors: {
      primary: {
        500: '#YOUR_COLOR',
        600: '#YOUR_COLOR',
        // ...
      }
    }
  }
}
```

### Adding New Pages

1. Create component in `src/pages/`
2. Add route in `src/App.tsx`
3. Add navigation item in `src/components/Layout.tsx`

### Modifying API Endpoints

Edit `src/services/api.ts` to add or modify API calls.

## Performance Tips

1. **Lazy Loading**: Use React.lazy() for code splitting
2. **Memoization**: Use useMemo and useCallback for expensive operations
3. **Virtual Scrolling**: For large lists, consider react-window
4. **Image Optimization**: Use WebP format and lazy loading

## Testing

### Manual Testing Checklist

- [ ] Dashboard loads with data
- [ ] Topics list displays correctly
- [ ] Topic details show statistics and posts
- [ ] Search functionality works
- [ ] Timeline visualization renders
- [ ] Scraper can fetch Reddit posts
- [ ] Navigation works smoothly
- [ ] Responsive design on mobile
- [ ] Error handling displays messages

### Browser Testing

Test on:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Deployment

### Option 1: Netlify

1. Build the project:
```bash
npm run build
```

2. Deploy `dist/` folder to Netlify

3. Configure redirects (create `public/_redirects`):
```
/*    /index.html   200
```

### Option 2: Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

### Option 3: GitHub Pages

1. Install gh-pages:
```bash
npm install --save-dev gh-pages
```

2. Add to package.json:
```json
{
  "scripts": {
    "deploy": "npm run build && gh-pages -d dist"
  }
}
```

3. Deploy:
```bash
npm run deploy
```

## Support

For issues or questions:
1. Check this setup guide
2. Review the main README.md
3. Check browser console for errors
4. Verify backend services are running
5. Review API documentation

## Next Steps

1. ✅ Install dependencies
2. ✅ Start backend services
3. ✅ Start frontend development server
4. ✅ Access application in browser
5. 🎉 Start developing!

---

**Happy Coding!** 🚀
