import { Hash, TrendingUp } from 'lucide-react';
import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { Link } from 'react-router-dom';
import { Badge, Card, EmptyState, LoadingSpinner } from '../components/UI';
import apiService from '../services/api';
import { Topic } from '../types';

const Topics = () => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState<'id' | 'count'>('count');

  useEffect(() => {
    loadTopics();
  }, []);

  const loadTopics = async () => {
    try {
      setLoading(true);
      const data = await apiService.getTopics();
      setTopics(data.topics);
    } catch (error) {
      toast.error('Failed to load topics');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const sortedTopics = [...topics].sort((a, b) => {
    if (sortBy === 'count') {
      return b.post_count - a.post_count;
    }
    return a.topic_id - b.topic_id;
  });

  if (loading) {
    return <LoadingSpinner size="lg" className="py-20" />;
  }

  if (topics.length === 0) {
    return (
      <EmptyState
        title="No Topics Found"
        description="Process the data first to detect topics"
        icon={<Hash size={48} />}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Topics</h1>
          <p className="mt-2 text-gray-600">
            Browse all detected topics from Reddit posts
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'id' | 'count')}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="count">Post Count</option>
            <option value="id">Topic ID</option>
          </select>
        </div>
      </div>

      {/* Topics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sortedTopics.map((topic) => (
          <Link key={topic.topic_id} to={`/topics/${topic.topic_id}`}>
            <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center">
                    <Hash className="w-6 h-6 text-primary-600" />
                  </div>
                  <Badge variant="info">ID: {topic.topic_id}</Badge>
                </div>
                <TrendingUp className="w-5 h-5 text-green-500" />
              </div>
              
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                {topic.topic_label}
              </h3>
              
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold text-primary-600">
                  {topic.post_count}
                </span>
                <span className="text-sm text-gray-500">posts</span>
              </div>
              
              <div className="mt-4 pt-4 border-t border-gray-100">
                <span className="text-sm text-primary-600 font-medium">
                  View Details →
                </span>
              </div>
            </Card>
          </Link>
        ))}
      </div>

      {/* Summary */}
      <Card>
        <div className="text-center">
          <p className="text-gray-600">
            Total <span className="font-semibold text-gray-900">{topics.length}</span> topics detected from{' '}
            <span className="font-semibold text-gray-900">
              {topics.reduce((sum, t) => sum + t.post_count, 0).toLocaleString()}
            </span>{' '}
            posts
          </p>
        </div>
      </Card>
    </div>
  );
};

export default Topics;
