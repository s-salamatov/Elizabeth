import { reactive, computed } from 'vue';
import api, { setAuthTokens, clearAuthTokens, getStoredTokens } from '../api/client';

const state = reactive({
  user: null,
  settings: null,
  tokens: null,
  initialized: false,
  loading: false,
  error: null,
});

export function useAuth() {
  const isAuthenticated = computed(() => Boolean(state.tokens?.access));

  const restore = async () => {
    if (state.initialized) return;
    const stored = getStoredTokens();
    if (stored) {
      state.tokens = stored;
      setAuthTokens(stored);
      try {
        const profile = await loadProfile();
        if (!profile) {
          clearAuthTokens();
          state.tokens = null;
        }
      } catch {
        clearAuthTokens();
        state.tokens = null;
      }
    }
    state.initialized = true;
  };

  const login = async (payload) => {
    state.loading = true;
    state.error = null;
    try {
      const { data } = await api.post('/auth/login', payload);
      state.tokens = data.tokens;
      setAuthTokens(data.tokens);
      state.user = data.user;
      await loadProfile();
      return true;
    } catch (error) {
      state.error =
        error.response?.data?.detail || 'Не удалось войти. Проверьте email и пароль.';
      return false;
    } finally {
      state.loading = false;
    }
  };

  const register = async (payload) => {
    state.loading = true;
    state.error = null;
    try {
      const { data } = await api.post('/auth/register', payload);
      state.tokens = data.tokens;
      setAuthTokens(data.tokens);
      state.user = data.user;
      await loadProfile();
      return true;
    } catch (error) {
      const respData = error.response?.data;
      if (respData?.phone_number) {
        state.error = 'Такой номер телефона уже используется.';
      } else {
        state.error =
          respData?.detail || 'Не удалось зарегистрироваться. Попробуйте ещё раз.';
      }
      return false;
    } finally {
      state.loading = false;
    }
  };

  const loadProfile = async () => {
    try {
      const { data } = await api.get('/auth/profile');
      state.user = data.user;
      state.settings = data.settings;
      return data;
    } catch {
      return null;
    }
  };

  const updateProfile = async (payload) => {
    state.loading = true;
    state.error = null;
    try {
      const { data } = await api.patch('/auth/profile', payload);
      state.user = data.user;
      state.settings = data.settings;
      return true;
    } catch (error) {
      state.error = error.response?.data?.detail || 'Не удалось сохранить профиль.';
      return false;
    } finally {
      state.loading = false;
    }
  };

  const deleteAccount = async () => {
    state.loading = true;
    state.error = null;
    try {
      await api.delete('/auth/profile/delete');
      logout();
      return true;
    } catch (error) {
      state.error = error.response?.data?.detail || 'Не удалось удалить профиль.';
      return false;
    } finally {
      state.loading = false;
    }
  };

  const logout = () => {
    state.user = null;
    state.settings = null;
    state.tokens = null;
    clearAuthTokens();
  };

  return {
    state,
    initialized: computed(() => state.initialized),
    isAuthenticated,
    login,
    register,
    logout,
    restore,
    loadProfile,
    updateProfile,
    deleteAccount,
  };
}
