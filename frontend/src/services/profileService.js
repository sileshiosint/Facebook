import apiClient from './api';

const getProfiles = async (params = {}) => {
  // Default pagination if not provided
  const queryParams = {
    skip: params.skip || 0,
    limit: params.limit || 10,
    ...params, // Add other filters like keyword
  };

  const response = await apiClient.get('/profiles/', { params: queryParams });
  return response.data; // Expects an object { data: [], total_count: 0 }
};

const getProfileById = async (profileId) => {
  const response = await apiClient.get(`/profiles/${profileId}`);
  return response.data; // Expects a single profile object
};

export default { getProfiles, getProfileById };
