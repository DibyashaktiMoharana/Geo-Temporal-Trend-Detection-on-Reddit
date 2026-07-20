import { AlertCircle, CheckCircle, Download, ExternalLink } from 'lucide-react';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { Badge, Card, LoadingSpinner } from '../components/UI';
import apiService from '../services/api';
import { ScrapedPost } from '../types';

const Scraper = () => {
  const [subreddit, setSubreddit] = useState('delhi');
  const [method, setMethod] = useState<'hot' | 'new' | 'top' | 'rising'>('hot');
  const [timeFilter, setTimeFilter] = useState<'day' | 'week' | 'month' | 'year' | 'all'>('month');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [scrapedPosts, setScrapedPosts] = useState<ScrapedPost[]>([]);
  const [loadingPosts, setLoadingPosts] = useState(false);

  const handleScrape = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!subreddit.trim()) {
      toast.error('Please enter a subreddit name');
      return;
    }

    try {
      setLoading(true);
      setResult(null);
      setScrapedPosts([]);
      
      // Step 1: Scrape Reddit posts
      toast.loading('Scraping Reddit posts...', { id: 'scrape' });
      const scrapeData = await apiService.scrapeReddit(subreddit.trim(), method, timeFilter);
      setResult(scrapeData);
      toast.success(`Successfully scraped ${scrapeData.data.posts_count} posts`, { id: 'scrape' });
      
      // Step 2: Fetch the scraped posts from database
      setLoadingPosts(true);
      toast.loading('Fetching scraped posts...', { id: 'fetch' });
      const postsData = await apiService.fetchScrapedPosts(subreddit.trim(), 10, 0);
      setScrapedPosts(postsData.data.posts);
      toast.success(`Loaded ${postsData.data.posts.length} posts`, { id: 'fetch' });
      
    } catch (error: any) {
      toast.error(error.response?.data?.message || error.message || 'Failed to scrape Reddit', { id: 'scrape' });
      toast.dismiss('fetch');
      console.error(error);
    } finally {
      setLoading(false);
      setLoadingPosts(false);
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
            <p className="text-sm text-gray-600 mb-2">
              This tool scrapes Reddit posts from the specified subreddit and saves them to a JSON file.
              Choose your preferred listing method and time filter to get relevant posts.
            </p>
            <ul className="text-sm text-gray-600 list-disc list-inside space-y-1">
              <li><strong>Hot:</strong> Currently trending posts</li>
              <li><strong>New:</strong> Recently posted content</li>
              <li><strong>Top:</strong> Highest scoring posts (uses time filter)</li>
              <li><strong>Rising:</strong> Posts gaining popularity</li>
            </ul>
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
                  <Badge variant="info">{result.data.listing_method}</Badge>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">Time Filter</p>
                  <Badge variant="default">{result.data.time_filter}</Badge>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">Posts Scraped</p>
                  <p className="text-2xl font-bold text-primary-600">
                    {result.data.posts_count.toLocaleString()}
                  </p>
                </div>
              </div>

              {result.data.json_file && (
                <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <span className="font-medium">File saved:</span> {result.data.json_file}
                  </p>
                </div>
              )}

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

      {/* Scraped Posts Display */}
      {loadingPosts && (
        <Card title="Loading Posts...">
          <LoadingSpinner size="lg" className="py-8" />
        </Card>
      )}

      {scrapedPosts.length > 0 && (
        <Card title={`Scraped Posts from r/${subreddit}`} subtitle={`Showing ${scrapedPosts.length} most recent posts`}>
          <div className="space-y-4">
            {scrapedPosts.map((post) => (
              <div
                key={post._id}
                className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:shadow-sm transition-all"
              >
                <div className="flex items-start justify-between gap-3 mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 flex-1">
                    {post.title}
                  </h3>
                  <Badge variant={post.upvote_ratio >= 0.8 ? 'success' : 'default'}>
                    {(post.upvote_ratio * 100).toFixed(0)}% upvoted
                  </Badge>
                </div>
                
                {post.selftext && (
                  <p className="text-sm text-gray-600 mb-3 line-clamp-3">
                    {post.selftext}
                  </p>
                )}
                
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <div className="flex items-center gap-4">
                    <span>Posted: {new Date(post.created_utc * 1000).toLocaleDateString()}</span>
                    <span>•</span>
                    <span>r/{post.subreddit}</span>
                  </div>
                  <a
                    href={`https://reddit.com${post.permalink}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-primary-600 hover:text-primary-700 font-medium"
                  >
                    View on Reddit
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

export default Scraper;
