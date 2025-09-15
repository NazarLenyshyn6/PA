const API_BASE_URL = 'http://localhost:8000';

export const apiEndpoints = {
  // Auth endpoints
  login: `${API_BASE_URL}/api/v1/auth/login`,
  register: `${API_BASE_URL}/api/v1/auth/register`,
  me: `${API_BASE_URL}/api/v1/auth/me`,

  // File endpoints
  files: `${API_BASE_URL}/api/v1/files`,
  fileUpload: `${API_BASE_URL}/api/v1/files`,
  filesMetadata: `${API_BASE_URL}/api/v1/files/metadata`,

  // Agent endpoint - streaming chat
  agentStream: `${API_BASE_URL}/api/v1/agent/stream`,
};

export const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  const tokenType = localStorage.getItem('token_type') || 'Bearer';
  return {
    'Authorization': `${tokenType} ${token}`,
    'Content-Type': 'application/json',
  };
};

export const apiRequest = async (url: string, options: RequestInit = {}) => {
  const defaultOptions: RequestInit = {
    mode: 'cors',
    credentials: 'include',
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    return response;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};