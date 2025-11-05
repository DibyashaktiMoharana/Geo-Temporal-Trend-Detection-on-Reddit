import { format } from 'date-fns';
import { ExternalLink, Filter, Search as SearchIcon } from 'lucide-react';
import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { Badge, Card, EmptyState, LoadingSpinner } from '../components/UI';
import apiService from '../services/api';
import { Post, Topic } from '../types';

const Search = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Post[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [selectedTopic, setSelectedTopic] = useState<number | undefined>();
  const [topics, setTopics] = useState<Topic[]>([]);
  const [limit, setLimit] = useState(20);

  useEffect(() => {
    loadTopics();
  }, []);

  const loadTopics = async () => {
    try {
      const data = await apiService.getTopics();
      setTopics(data.topics);
    } catch (error) {
      console.error('Failed to load topics:', error);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    try {
      setLoading(true);
      setSearched(true);
      const data = await apiService.search(query, selectedTopic, limit);
      setResults(data.results);
      toast.success(`Found ${data.total_results} results`);
    } catch (error) {
      toast.error('Search failed');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Search Posts</h1>
        <p className="mt-2 text-gray-600">
          Search across all Reddit posts by keywords and filters
        </p>
      </div>

      {/* Search Form */}
      <Card>
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter search keywords..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>

          {/* Filters */}
          <div className="flex items-center gap-4 pt-4 border-t">
            <Filter className="w-5 h-5 text-gray-400" />
            <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Filter by Topic
                </label>
                <select
                  value={selectedTopic || ''}
                  onChange={(e) =>
                    setSelectedTopic(e.target.value ? parseInt(e.target.value) : undefined)
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">All Topics</option>
                  {topics.map((topic) => (
                    <option key={topic.topic_id} value={topic.topic_id}>
                      {topic.topic_label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Result Limit
                </label>
                <select
                  value={limit}
                  onChange={(e) => setLimit(parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="10">10 results</option>
                  <option value="20">20 results</option>
                  <option value="50">50 results</option>
                  <option value="100">100 results</option>
                </select>
              </div>
            </div>
          </div>
        </form>
      </Card>

      {/* Loading State */}
      {loading && <LoadingSpinner size="lg" className="py-12" />}

      {/* Results */}
      {!loading && searched && (
        <>
          {results.length === 0 ? (
            <EmptyState
              title="No Results Found"
              description="Try adjusting your search query or filters"
              icon={<SearchIcon size={48} />}
            />
          ) : (
            <Card title={`Search Results (${results.length})`}>
              <div className="space-y-4">
                {results.map((post) => (
                  <div
                    key={post._id}
                    className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-gray-900 flex-1">
                        {post.title}
                      </h3>
                      <div className="flex items-center space-x-2 ml-4">
                        {post.topic_label && (
                          <Badge variant="info" size="sm">
                            {post.topic_label}
                          </Badge>
                        )}
                        {post.upvote_ratio && (
                          <Badge variant="success" size="sm">
                            {(post.upvote_ratio * 100).toFixed(0)}%
                          </Badge>
                        )}
                      </div>
                    </div>

                    {(post.text || post.selftext) && (
                      <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                        {post.text || post.selftext}
                      </p>
                    )}

                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        {post.score !== undefined && (
                          <span>Score: {post.score}</span>
                        )}
                        {post.num_comments !== undefined && (
                          <span>{post.num_comments} comments</span>
                        )}
                        {post.created_utc && (
                          <span>
                            {format(new Date(post.created_utc), 'MMM d, yyyy')}
                          </span>
                        )}
                      </div>
                      <a
                        href={`https://reddit.com${post.permalink}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center text-sm text-primary-600 hover:text-primary-700"
                      >
                        View on Reddit
                        <ExternalLink className="w-3 h-3 ml-1" />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );
};

export default Search;
