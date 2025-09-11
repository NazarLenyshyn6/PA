const API_BASE_URL = 'http://localhost:8000';

export const apiEndpoints = {
  login: `${API_BASE_URL}/api/v1/auth/login`,
  register: `${API_BASE_URL}/api/v1/auth/register`,
  files: `${API_BASE_URL}/api/v1/files`,
  fileUpload: `${API_BASE_URL}/api/v1/files`,
  sessions: `${API_BASE_URL}/api/v1/sessions`,
  // Agent endpoint - streaming chat
  agentStream: `${API_BASE_URL}/api/v1/agent/stream`,
  // Note: Legacy chat endpoints below don't exist in current energy_agent backend
  chat: `${API_BASE_URL}/api/v1/chat`,
  chatSave: `${API_BASE_URL}/api/v1/chat/save`,
  chatHistory: `${API_BASE_URL}/api/v1/chat/history`,
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