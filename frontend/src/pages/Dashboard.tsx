import { Activity, Hash, MessageSquare, TrendingUp } from 'lucide-react';
import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { Link } from 'react-router-dom';
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import { Card, EmptyState, LoadingSpinner, StatCard } from '../components/UI';
import apiService from '../services/api';
import { Statistics, TopicDistribution } from '../types';

const Dashboard = () => {
  const [stats, setStats] = useState<Statistics | null>(null);
  const [distribution, setDistribution] = useState<TopicDistribution[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsData, distData] = await Promise.all([
        apiService.getStatistics(),
        apiService.getTopicDistribution(),
      ]);
      setStats(statsData.statistics);
      // Safely handle distribution data with null checks
      const distArray = distData?.distribution || [];
      setDistribution(Array.isArray(distArray) ? distArray.slice(0, 8) : []); // Top 8 topics
    } catch (error) {
      toast.error('Failed to load dashboard data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const COLORS = [
    '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
    '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'
  ];

  if (loading) {
    return <LoadingSpinner size="lg" className="py-20" />;
  }

  if (!stats) {
    return (
      <EmptyState
        title="No Data Available"
        description="Process the data first to see the dashboard"
        action={{
          label: 'Process Data',
          onClick: async () => {
            try {
              await apiService.processData();
              toast.success('Data processing started');
            } catch (error) {
              toast.error('Failed to start processing');
            }
          },
        }}
      />
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Overview of Reddit trend analysis and topic detection
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Posts"
          value={(stats.total_posts || 0).toLocaleString()}
          icon={<TrendingUp className="w-6 h-6 text-primary-600" />}
        />
        <StatCard
          title="Topics Detected"
          value={stats.total_topics || 0}
          icon={<Hash className="w-6 h-6 text-primary-600" />}
        />
        <StatCard
          title="Total Comments"
          value={(stats.total_comments || 0).toLocaleString()}
          icon={<MessageSquare className="w-6 h-6 text-primary-600" />}
        />
        <StatCard
          title="Avg Upvote Ratio"
          value={stats.avg_upvote_ratio ? (stats.avg_upvote_ratio * 100).toFixed(1) + '%' : '0%'}
          icon={<Activity className="w-6 h-6 text-primary-600" />}
        />
      </div>

      {/* Charts and Top Topics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Topic Distribution Chart */}
        <Card title="Topic Distribution" subtitle="Top 8 topics by post count">
          {distribution && distribution.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={distribution}
                  dataKey="count"
                  nameKey="topic_label"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={(entry) => entry?.percentage ? `${entry.percentage.toFixed(1)}%` : ''}
                >
                  {distribution.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value: any, name: string) => [
                    `${value} posts`,
                    name || 'Unknown'
                  ]}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-gray-500">
              <div className="text-center">
                <Hash className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                <p>No topic distribution data available</p>
              </div>
            </div>
          )}
        </Card>

        {/* Top Topics List */}
        <Card title="Top Topics" subtitle="Most discussed topics">
          <div className="space-y-3">
            {stats.top_topics && Array.isArray(stats.top_topics) && stats.top_topics.length > 0 ? (
              stats.top_topics.map((topic, index) => (
                <Link
                  key={topic.topic}
                  to={`/topics/${topic.topic}`}
                  className="block p-4 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                        <span className="text-sm font-bold text-primary-600">
                          #{index + 1}
                        </span>
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900">
                          {topic.topic_label || 'Unknown Topic'}
                        </h4>
                        <p className="text-sm text-gray-500">
                          {topic.count || 0} posts
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium text-primary-600">
                        View Details →
                      </div>
                    </div>
                  </div>
                </Link>
              ))
            ) : (
              <div className="flex items-center justify-center py-8 text-gray-500">
                <div className="text-center">
                  <Hash className="w-10 h-10 mx-auto mb-2 text-gray-400" />
                  <p>No topics available</p>
                </div>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Date Range Info */}
      {stats.date_range && stats.date_range.start && stats.date_range.end && (
        <Card title="Data Range">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Start Date</p>
              <p className="text-lg font-semibold text-gray-900">
                {new Date(stats.date_range.start).toLocaleDateString()}
              </p>
            </div>
            <div className="text-center">
              <div className="text-primary-600">
                <Activity className="w-8 h-8 mx-auto" />
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">End Date</p>
              <p className="text-lg font-semibold text-gray-900">
                {new Date(stats.date_range.end).toLocaleDateString()}
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default Dashboard;
