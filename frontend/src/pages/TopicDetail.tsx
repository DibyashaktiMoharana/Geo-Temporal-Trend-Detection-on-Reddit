import { format } from 'date-fns';
import { ArrowLeft, ExternalLink, MessageSquare, TrendingUp } from 'lucide-react';
import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { Link, useParams } from 'react-router-dom';
import { Badge, Card, EmptyState, LoadingSpinner } from '../components/UI';
import apiService from '../services/api';
import { TopicDetail as TopicDetailType } from '../types';

const TopicDetail = () => {
  const { topicId } = useParams<{ topicId: string }>();
  const [topic, setTopic] = useState<TopicDetailType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (topicId) {
      loadTopic(parseInt(topicId));
    }
  }, [topicId]);

  const loadTopic = async (id: number) => {
    try {
      setLoading(true);
      const data = await apiService.getTopicDetail(id);
      setTopic(data);
    } catch (error) {
      toast.error('Failed to load topic details');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner size="lg" className="py-20" />;
  }

  if (!topic) {
    return (
      <EmptyState
        title="Topic Not Found"
        description="The requested topic could not be found"
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <Link
          to="/topics"
          className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Topics
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <h1 className="text-3xl font-bold text-gray-900">
                {topic.topic_label}
              </h1>
              <Badge variant="info">Topic #{topic.topic_id}</Badge>
            </div>
            <p className="text-gray-600">
              Detailed analysis and representative posts
            </p>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-2">Total Posts</p>
            <p className="text-3xl font-bold text-primary-600">
              {topic.statistics.total_posts}
            </p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-2">Avg Upvote Ratio</p>
            <p className="text-3xl font-bold text-green-600">
              {(topic.statistics.avg_upvote_ratio * 100).toFixed(1)}%
            </p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-2">Avg Comments</p>
            <p className="text-3xl font-bold text-blue-600">
              {topic.statistics.avg_comments.toFixed(1)}
            </p>
          </div>
        </Card>
      </div>

      {/* Representative Posts */}
      <Card title="Representative Posts" subtitle="Most characteristic posts for this topic">
        <div className="space-y-4">
          {topic.representative_posts.map((post, index) => (
            <div
              key={post.id}
              className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors"
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                  <span className="text-sm font-bold text-primary-600">
                    {index + 1}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-semibold text-gray-900 mb-2">
                    {post.title}
                  </h4>
                  <p className="text-gray-600 text-sm line-clamp-3">
                    {post.text}
                  </p>
                  <a
                    href={`https://reddit.com${post.permalink}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center mt-2 text-sm text-primary-600 hover:text-primary-700"
                  >
                    View on Reddit
                    <ExternalLink className="w-3 h-3 ml-1" />
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Top Recent Posts */}
      <Card title="Recent Popular Posts" subtitle="Latest posts in this topic">
        <div className="space-y-4">
          {topic.top_posts.map((post) => (
            <div
              key={post._id}
              className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-semibold text-gray-900 flex-1">
                  {post.title}
                </h4>
                <Badge variant="success" size="sm">
                  {(post.upvote_ratio * 100).toFixed(0)}%
                </Badge>
              </div>
              
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <span className="flex items-center">
                  <TrendingUp className="w-4 h-4 mr-1" />
                  {post.upvote_ratio.toFixed(2)}
                </span>
                {post.num_comments !== undefined && (
                  <span className="flex items-center">
                    <MessageSquare className="w-4 h-4 mr-1" />
                    {post.num_comments} comments
                  </span>
                )}
                <span>
                  {format(new Date(post.created_utc), 'MMM d, yyyy')}
                </span>
              </div>
              
              <a
                href={`https://reddit.com${post.permalink}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center mt-2 text-sm text-primary-600 hover:text-primary-700"
              >
                View on Reddit
                <ExternalLink className="w-3 h-3 ml-1" />
              </a>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

export default TopicDetail;
