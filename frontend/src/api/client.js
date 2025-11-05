import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

export const chatAPI = {
  // Start a new conversation
  startConversation: async () => {
    const response = await api.post('/chat/start');
    return response.data;
  },

  // Send a message
  sendMessage: async (sessionId, message) => {
    const response = await api.post('/chat/message', {
      session_id: sessionId,
      message: message,
    });
    return response.data;
  },

  // Escalate conversation
  escalateConversation: async (sessionId, userQuery) => {
    const response = await api.post('/chat/escalate', {
      session_id: sessionId,
      user_query: userQuery,
    });
    return response.data;
  },

  // Get conversation history
  getHistory: async (sessionId) => {
    const response = await api.get(`/chat/history/${sessionId}`);
    return response.data;
  },

  // Get available topics
  getTopics: async () => {
    const response = await api.get('/topics');
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
