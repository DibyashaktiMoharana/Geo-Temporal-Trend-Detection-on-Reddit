import { Calendar } from 'lucide-react';
import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Card, EmptyState, LoadingSpinner } from '../components/UI';
import apiService from '../services/api';
import { TimelineData } from '../types';

const Timeline = () => {
  const [timelineData, setTimelineData] = useState<TimelineData | null>(null);
  const [loading, setLoading] = useState(true);
  const [interval, setInterval] = useState<'day' | 'week' | 'month'>('week');

  useEffect(() => {
    loadTimeline();
  }, [interval]);

  const loadTimeline = async () => {
    try {
      setLoading(true);
      const data = await apiService.getTimeline(interval);
      setTimelineData(data);
    } catch (error) {
      toast.error('Failed to load timeline data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner size="lg" className="py-20" />;
  }

  if (!timelineData || !timelineData.timeline || timelineData.timeline.length === 0) {
    return (
      <EmptyState
        title="No Timeline Data"
        description="No data available for the selected time interval"
        icon={<Calendar size={48} />}
      />
    );
  }

  // Group timeline data by date
  const groupedByDate = timelineData.timeline.reduce((acc: any, item) => {
    if (!item.date) return acc;
    
    if (!acc[item.date]) {
      acc[item.date] = {
        date: item.date,
        topics: [],
        total: 0,
      };
    }
    
    if (item.topic_label && item.count) {
      acc[item.date].topics.push({
        topic: item.topic,
        topic_label: item.topic_label,
        count: item.count,
      });
      acc[item.date].total += item.count;
    }
    
    return acc;
  }, {});

  // Convert to array and sort by date
  const groupedTimeline = Object.values(groupedByDate).sort(
    (a: any, b: any) => new Date(a.date).getTime() - new Date(b.date).getTime()
  );

  // Prepare data for chart - group by date and add top 5 topics
  const chartData = groupedTimeline.map((item: any) => {
    const dataPoint: any = {
      date: item.date ? new Date(item.date).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      }) : 'Unknown',
      total: item.total || 0,
    };
    
    // Add top 5 topics to the chart
    if (item.topics && Array.isArray(item.topics)) {
      item.topics
        .sort((a: any, b: any) => b.count - a.count)
        .slice(0, 5)
        .forEach((topic: any) => {
          if (topic && topic.topic_label) {
            dataPoint[topic.topic_label] = topic.count || 0;
          }
        });
    }
    
    return dataPoint;
  });

  // Get all unique topic labels for the legend (top 5 overall)
  const topicCounts = new Map<string, number>();
  timelineData.timeline.forEach((item) => {
    if (item.topic_label && item.count) {
      const current = topicCounts.get(item.topic_label) || 0;
      topicCounts.set(item.topic_label, current + item.count);
    }
  });
  
  const topicLabels = Array.from(topicCounts.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([label]) => label);

  // Calculate date range from data
  const dates = groupedTimeline.map((item: any) => new Date(item.date));
  const startDate = dates.length > 0 ? new Date(Math.min(...dates.map(d => d.getTime()))) : null;
  const endDate = dates.length > 0 ? new Date(Math.max(...dates.map(d => d.getTime()))) : null;

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Timeline</h1>
          <p className="mt-2 text-gray-600">
            Topic distribution over time
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">Interval:</span>
          <select
            value={interval}
            onChange={(e) => setInterval(e.target.value as 'day' | 'week' | 'month')}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="day">Daily</option>
            <option value="week">Weekly</option>
            <option value="month">Monthly</option>
          </select>
        </div>
      </div>

      {/* Date Range */}
      {startDate && endDate && (
        <Card>
          <div className="flex items-center justify-center space-x-4 text-sm text-gray-600">
            <span>
              From: <strong>{startDate.toLocaleDateString()}</strong>
            </span>
            <span>•</span>
            <span>
              To: <strong>{endDate.toLocaleDateString()}</strong>
            </span>
          </div>
        </Card>
      )}

      {/* Timeline Chart */}
      <Card title="Topic Trends" subtitle="Top 5 topics over time">
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            {Array.from(topicLabels).map((label, index) => (
              <Bar
                key={label}
                dataKey={label}
                stackId="a"
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </Card>

      {/* Timeline Details */}
      <Card title="Detailed Breakdown">
        <div className="space-y-4">
          {groupedTimeline.map((item: any, index: number) => (
            <div
              key={index}
              className="p-4 border border-gray-200 rounded-lg"
            >
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-gray-900">
                  {new Date(item.date).toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </h4>
                <span className="text-sm font-medium text-primary-600">
                  {item.total} posts
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                {item.topics && Array.isArray(item.topics) && item.topics.length > 0 ? (
                  item.topics
                    .sort((a: any, b: any) => b.count - a.count)
                    .map((topic: any) => (
                      <div
                        key={topic.topic}
                        className="flex items-center justify-between px-3 py-2 bg-gray-50 rounded"
                      >
                        <span className="text-sm text-gray-700 truncate">
                          {topic.topic_label}
                        </span>
                        <span className="text-sm font-medium text-gray-900 ml-2">
                          {topic.count}
                        </span>
                      </div>
                    ))
                ) : (
                  <div className="col-span-3 text-sm text-gray-500 text-center py-2">
                    No topics available for this period
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

export default Timeline;
