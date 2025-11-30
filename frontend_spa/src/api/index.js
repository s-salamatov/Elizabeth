import api from './client';

export const AuthApi = {
  login: (payload) => api.post('/auth/login', payload),
  register: (payload) => api.post('/auth/register', payload),
  me: () => api.get('/auth/me'),
  updateProfile: (payload) => api.patch('/auth/me', payload),
};

export const SearchApi = {
  bulk: (payload) => api.post('/search/bulk', payload),
  list: () => api.get('/search/'),
  detail: (id) => api.get(`/search/${id}`),
};

export const ProductApi = {
  requestDetails: (productIds) => api.post('/products/details/request', { product_ids: productIds }),
  pollStatus: (requestIds) => api.post('/products/details/status', { request_ids: requestIds }),
};

export const ProviderApi = {
  accounts: () => api.get('/providers/'),
  armtekCredentials: () => api.get('/providers/armtek/credentials'),
  saveArmtek: (payload) => api.post('/providers/armtek/credentials', payload),
  deleteArmtek: () => api.delete('/providers/armtek/credentials'),
};
