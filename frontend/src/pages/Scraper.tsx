import { AlertCircle, CheckCircle, Download } from 'lucide-react';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { Badge, Card, LoadingSpinner } from '../components/UI';
import apiService from '../services/api';

const Scraper = () => {
  const [subreddit, setSubreddit] = useState('delhi');
  const [method, setMethod] = useState<'hot' | 'new' | 'top' | 'rising'>('hot');
  const [timeFilter, setTimeFilter] = useState<'day' | 'week' | 'month' | 'year' | 'all'>('month');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleScrape = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!subreddit.trim()) {
      toast.error('Please enter a subreddit name');
      return;
    }

    try {
      setLoading(true);
      setResult(null);
      const data = await apiService.scrapeReddit(subreddit.trim(), method, timeFilter);
      setResult(data);
      toast.success(`Successfully scraped ${data.data.posts_saved} posts`);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to scrape Reddit');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Reddit Scraper</h1>
        <p className="mt-2 text-gray-600">
          Scrape posts from Reddit subreddits for analysis
        </p>
      </div>

      {/* Info Alert */}
      <Card>
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="font-semibold text-gray-900 mb-1">How it works</h4>
            <p className="text-sm text-gray-600">
              This tool scrapes Reddit posts from the specified subreddit and stores them in the database.
              For 'hot', 'new', and 'rising' methods, all posts from the last 6 months are fetched.
              The 'top' method uses the time filter you select.
            </p>
          </div>
        </div>
      </Card>

      {/* Scraper Form */}
      <Card title="Scrape Configuration">
        <form onSubmit={handleScrape} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Subreddit Name
            </label>
            <input
              type="text"
              value={subreddit}
              onChange={(e) => setSubreddit(e.target.value)}
              placeholder="e.g., delhi, pune, bangalore"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              disabled={loading}
            />
            <p className="mt-1 text-xs text-gray-500">
              Enter the subreddit name without 'r/' prefix
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Listing Method
              </label>
              <select
                value={method}
                onChange={(e) => setMethod(e.target.value as any)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                disabled={loading}
              >
                <option value="hot">Hot</option>
                <option value="new">New</option>
                <option value="top">Top</option>
                <option value="rising">Rising</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Time Filter {method !== 'top' && '(only for "top" method)'}
              </label>
              <select
                value={timeFilter}
                onChange={(e) => setTimeFilter(e.target.value as any)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                disabled={loading || method !== 'top'}
              >
                <option value="day">Day</option>
                <option value="week">Week</option>
                <option value="month">Month</option>
                <option value="year">Year</option>
                <option value="all">All Time</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <>
                <LoadingSpinner size="sm" className="mr-2" />
                Scraping...
              </>
            ) : (
              <>
                <Download className="w-5 h-5 mr-2" />
                Start Scraping
              </>
            )}
          </button>
        </form>
      </Card>

      {/* Results */}
      {result && (
        <Card>
          <div className="flex items-start space-x-3">
            <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="font-semibold text-gray-900 mb-3">Scraping Complete</h4>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">Subreddit</p>
                  <p className="font-semibold text-gray-900">r/{result.data.subreddit}</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">Method</p>
                  <Badge variant="info">{result.data.method}</Badge>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">Time Filter</p>
                  <Badge variant="default">{result.data.time_filter}</Badge>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">Posts Saved</p>
                  <p className="text-2xl font-bold text-primary-600">
                    {result.data.posts_saved}
                  </p>
                </div>
              </div>

              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-800">
                  ✓ {result.message}
                </p>
                <p className="text-xs text-green-600 mt-1">
                  Run the analysis model to process these posts and detect topics.
                </p>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default Scraper;
