import apiClient from './api';

const getPosts = async (filters = {}) => {
  // Prepare parameters, ensuring skip and limit are present
  const params = {
    skip: filters.skip || 0,
    limit: filters.limit || 10,
  };

  // Add other filter parameters if they are provided and not empty
  if (filters.keyword) params.keyword = filters.keyword;
  if (filters.min_risk_score !== undefined && filters.min_risk_score !== '' && filters.min_risk_score !== null) {
    params.min_risk_score = filters.min_risk_score;
  }
  if (filters.language) params.language = filters.language;
  if (filters.source_type) params.source_type = filters.source_type;
  if (filters.group_url) params.group_url = filters.group_url;
  if (filters.page_url) params.page_url = filters.page_url;
  if (filters.date_from) params.date_from = filters.date_from; // Expects ISO string
  if (filters.date_to) params.date_to = filters.date_to;     // Expects ISO string
  if (filters.entity_text) params.entity_text = filters.entity_text;
  if (filters.entity_label) params.entity_label = filters.entity_label;
  if (filters.sort_by) params.sort_by = filters.sort_by;
  if (filters.sort_order) params.sort_order = filters.sort_order;


  // console.log("Requesting posts with params:", params);
  const response = await apiClient.get('/posts/', { params });
  // The backend is expected to return a list of posts directly.
  // If it returns an object like { items: [], total: ... }, adjust accordingly.
  return response.data;
};

const getPostById = async (postId) => {
  const response = await apiClient.get(`/posts/${postId}`);
  return response.data; // Expects a single post object
};

export default {
    getPosts,
    getPostById
    // Analytics functions removed, now in analyticsService.js
};
