import apiClient from './api';

const getRiskCategories = async () => {
  const response = await apiClient.get('/analytics/risk_categories/');
  return response.data;
};

const getTopEntities = async (params = { n: 10 }) => {
  // Ensure entity_label is only added if it has a value
  const queryParams = { n: params.n };
  if (params.entity_label) {
    queryParams.entity_label = params.entity_label;
  }
  const response = await apiClient.get('/analytics/top_entities/', { params: queryParams });
  return response.data;
};

const getLanguageDistribution = async () => {
  const response = await apiClient.get('/analytics/language_distribution/');
  return response.data;
};

const getPostsTimeSeries = async (params = { interval: 'day' }) => {
  const response = await apiClient.get('/analytics/posts_time_series/', { params });
  return response.data;
};

export default {
  getRiskCategories,
  getTopEntities,
  getLanguageDistribution,
  getPostsTimeSeries,
};
