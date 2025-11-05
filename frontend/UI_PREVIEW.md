# Frontend UI Preview Guide

## 🎨 Page Layouts

### 1. Dashboard Page (`/`)

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Reddit Trends                                    [☰ Menu]  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Dashboard                                                    │
│  Overview of Reddit trend analysis and topic detection       │
│                                                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ Total Posts │ │   Topics    │ │   Comments  │           │
│  │   12,345    │ │     15      │ │   45,678    │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                               │
│  ┌────────────────────────┐  ┌─────────────────────────┐   │
│  │  Topic Distribution    │  │    Top Topics           │   │
│  │  [Pie Chart]           │  │  1. Traffic Issues      │   │
│  │                        │  │  2. Air Quality         │   │
│  │                        │  │  3. Metro Updates       │   │
│  └────────────────────────┘  └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- 4 stat cards at the top
- Interactive pie chart
- Clickable topic cards
- Date range information

---

### 2. Topics Page (`/topics`)

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Topics                                      Sort: [Count ▼] │
│  Browse all detected topics from Reddit posts                │
│                                                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ #  Topic 0  │ │ #  Topic 1  │ │ #  Topic 2  │           │
│  │             │ │             │ │             │           │
│  │ Traffic     │ │ Air Quality │ │ Metro       │           │
│  │ Issues      │ │ Issues      │ │ Services    │           │
│  │             │ │             │ │             │           │
│  │ 125 posts   │ │ 98 posts    │ │ 87 posts    │           │
│  │             │ │             │ │             │           │
│  │ View →      │ │ View →      │ │ View →      │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                               │
│  [More topic cards...]                                       │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Grid layout of topic cards
- Sort by count or ID
- Visual badges
- Click to view details

---

### 3. Topic Detail Page (`/topics/:id`)

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  ← Back to Topics                                            │
│                                                               │
│  Traffic and Transportation Issues            Topic #0       │
│  Detailed analysis and representative posts                  │
│                                                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ Total Posts │ │ Avg Upvote  │ │ Avg Comments│           │
│  │    125      │ │    87%      │ │    23.5     │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                               │
│  Representative Posts                                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 1  Ring Road Traffic Nightmare                        │  │
│  │    The traffic on Ring Road is getting worse...       │  │
│  │    View on Reddit →                                    │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ 2  [Another representative post...]                   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  Recent Popular Posts                                         │
│  [List of recent posts with scores and comments]             │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Statistics cards
- Representative posts (5)
- Recent posts list
- Reddit links

---

### 4. Search Page (`/search`)

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Search Posts                                                 │
│  Search across all Reddit posts by keywords and filters      │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 🔍 [Enter search keywords...]        [Search]         │  │
│  │                                                        │  │
│  │ Filter by Topic: [All Topics ▼]  Limit: [20 ▼]       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  Search Results (15)                                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Post Title Here                            [Badge]     │  │
│  │ Post content preview text goes here...                │  │
│  │ Score: 123 | 45 comments | Nov 4, 2025                │  │
│  │ View on Reddit →                                       │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │ [More search results...]                              │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Search input with filters
- Topic filter dropdown
- Result limit selector
- Rich result cards

---

### 5. Timeline Page (`/timeline`)

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Timeline                                Interval: [Week ▼]  │
│  Topic distribution over time                                │
│                                                               │
│  From: Jan 1, 2025 • To: Nov 5, 2025                        │
│                                                               │
│  Topic Trends                                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                 [Stacked Bar Chart]                    │  │
│  │  100│     ███                                          │  │
│  │   75│    ████  ███                                     │  │
│  │   50│   █████ █████  ███                               │  │
│  │   25│  ██████████████████                              │  │
│  │    0└────────────────────────────────────────         │  │
│  │      Jan   Feb   Mar   Apr   May                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  Detailed Breakdown                                           │
│  [Date-wise topic breakdowns...]                             │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Interval selector (day/week/month)
- Interactive stacked bar chart
- Date range display
- Detailed breakdowns

---

### 6. Scraper Page (`/scraper`)

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Reddit Scraper                                               │
│  Scrape posts from Reddit subreddits for analysis           │
│                                                               │
│  ℹ️ How it works                                             │
│  This tool scrapes Reddit posts from the specified          │
│  subreddit and stores them in the database.                 │
│                                                               │
│  Scrape Configuration                                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Subreddit Name                                         │  │
│  │ [delhi                                    ]            │  │
│  │                                                        │  │
│  │ Listing Method:  [Hot ▼]  Time Filter: [Month ▼]     │  │
│  │                                                        │  │
│  │              [🔽 Start Scraping]                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  ✅ Scraping Complete                                        │
│  r/delhi | Hot | Month | 245 posts saved                    │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Subreddit input
- Method selector
- Time filter
- Success feedback

---

## 🎨 Color Scheme

**Primary Colors:**
- Primary Blue: `#3b82f6`
- Success Green: `#10b981`
- Warning Amber: `#f59e0b`
- Error Red: `#ef4444`

**Background:**
- Light Gray: `#f9fafb`
- White: `#ffffff`
- Dark Text: `#111827`

## 📱 Responsive Breakpoints

- **Desktop:** 1024px+
- **Tablet:** 768px - 1024px
- **Mobile:** 320px - 768px

## 🎯 Navigation Sidebar

```
┌─────────────────┐
│  Reddit Trends  │
├─────────────────┤
│ 📊 Dashboard    │
│ #  Topics       │
│ 🔍 Search       │
│ 📈 Timeline     │
│ 🌐 Scraper      │
├─────────────────┤
│ Geo-Temporal    │
│ Trend Detection │
└─────────────────┘
```

**Active State:** Blue background with darker blue text
**Hover State:** Light gray background

## ✨ Interactive Elements

### Buttons
- **Primary:** Blue background, white text
- **Hover:** Darker blue
- **Disabled:** 50% opacity

### Cards
- **Default:** White background, shadow
- **Hover:** Larger shadow
- **Active:** Blue border

### Badges
- **Info:** Blue background
- **Success:** Green background
- **Warning:** Yellow background
- **Default:** Gray background

## 🔄 Loading States

```
    ⏳
  Loading...
```

Spinner with rotating animation

## ❌ Empty States

```
    📄
  No Data Available
  Description text here
  [Action Button]
```

Icon, title, description, and optional action

## 🎉 Notifications (Toast)

```
┌─────────────────────────────┐
│ ✅ Success message here     │
└─────────────────────────────┘

┌─────────────────────────────┐
│ ❌ Error message here       │
└─────────────────────────────┘
```

Appears top-right, auto-dismisses

---

This preview guide helps you visualize the complete frontend before running it!
