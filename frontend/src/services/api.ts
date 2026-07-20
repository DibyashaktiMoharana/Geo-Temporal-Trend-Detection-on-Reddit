import axios from 'axios';
import {
    FetchPostsResult,
    HealthStatus,
    ScrapeResult,
    SearchResult,
    Statistics,
    TimelineData,
    Topic,
    TopicDetail,
    TopicDistribution,
} from '../types';

// Use production API or fallback to local proxy
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://reddit-trend-analysis-api.onrender.com/api';
const SCRAPER_BASE_URL = '/scrape/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const scraperApi = axios.create({
  baseURL: SCRAPER_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Health and Status
  async getHealth(): Promise<HealthStatus> {
    const { data } = await api.get('/health');
    return data;
  },

  async getProcessingStatus() {
    const { data } = await api.get('/processing-status');
    return data;
  },

  async processData() {
    const { data } = await api.post('/process');
    return data;
  },

  async reloadData() {
    const { data } = await api.post('/reload');
    return data;
  },

  // Topics
  async getTopics(): Promise<{ success: boolean; total_topics: number; topics: Topic[] }> {
    const { data } = await api.get('/topics');
    return data;
  },

  async getTopicDetail(topicId: number): Promise<TopicDetail> {
    const { data } = await api.get(`/topic/${topicId}`);
    return data;
  },

  async getTopicDistribution(): Promise<{ success: boolean; distribution: TopicDistribution[] }> {
    const { data } = await api.get('/topic-distribution');
    return data;
  },

  // Statistics
  async getStatistics(): Promise<{ success: boolean; statistics: Statistics }> {
    const { data } = await api.get('/stats');
    return data;
  },

  // Timeline
  async getTimeline(interval: 'day' | 'week' | 'month' = 'week'): Promise<TimelineData> {
    const { data } = await api.get('/timeline', {
      params: { interval },
    });
    return data;
  },

  // Search
  async search(query: string, topic?: number, limit: number = 20): Promise<SearchResult> {
    const { data } = await api.get('/search', {
      params: { q: query, topic, limit },
    });
    return data;
  },

  // Scraper
  async scrapeReddit(
    subreddit: string,
    method: 'hot' | 'new' | 'top' | 'rising' = 'hot',
    timeFilter: 'day' | 'week' | 'month' | 'year' | 'all' = 'month'
  ): Promise<ScrapeResult> {
    const { data } = await scraperApi.get('/scrape', {
      params: {
        subreddit,
        method,
        time_filter: timeFilter,
      },
    });
    return data;
  },

  async getScraperHealth() {
    const { data } = await scraperApi.get('/health');
    return data;
  },

  // Fetch scraped posts
  async fetchScrapedPosts(
    subreddit: string,
    limit: number = 10,
    skip: number = 0
  ): Promise<FetchPostsResult> {
    const { data } = await scraperApi.get('/posts/', {
      params: {
        subreddit,
        limit,
        skip,
      },
    });
    return data;
  },
};

export default apiService;
