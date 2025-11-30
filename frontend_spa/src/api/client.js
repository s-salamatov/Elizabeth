import axios from 'axios';

const STORAGE_KEY = 'elizabeth_tokens';

let accessToken = null;
let refreshToken = null;

const api = axios.create({
  baseURL: '/api/v1',
});

api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

export function setAuthTokens(tokens) {
  accessToken = tokens?.access ?? null;
  refreshToken = tokens?.refresh ?? null;
  if (tokens) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tokens));
  }
}

export function clearAuthTokens() {
  accessToken = null;
  refreshToken = null;
  localStorage.removeItem(STORAGE_KEY);
}

export function getStoredTokens() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch (error) {
    return null;
  }
}

export default api;
