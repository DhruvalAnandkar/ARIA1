import axios from "axios";
import { BACKEND_URL } from "../constants/config";
import { getToken, removeToken, removeUser } from "../utils/storage";

const api = axios.create({
  baseURL: BACKEND_URL,
  timeout: 10000,
});

// Attach auth token to every request
api.interceptors.request.use(async (config) => {
  const token = await getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await removeToken();
      await removeUser();
      // The auth store will detect the missing token and redirect to login
    }
    return Promise.reject(error);
  }
);

export default api;
