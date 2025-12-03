import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import SearchView from '../views/SearchView.vue';
import RequestsView from '../views/RequestsView.vue';
import SettingsView from '../views/SettingsView.vue';
import { useAuth } from '../stores/useAuth';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
    { path: '/register', name: 'register', component: RegisterView, meta: { public: true } },
    {
      path: '/register/details',
      name: 'register-details',
      component: RegisterView,
      meta: { public: true },
    },
    { path: '/', redirect: '/search' },
    { path: '/search', name: 'search', component: SearchView, meta: { requiresAuth: true } },
    { path: '/requests', name: 'requests', component: RequestsView, meta: { requiresAuth: true } },
    { path: '/settings', name: 'settings', component: SettingsView, meta: { requiresAuth: true } },
  ],
});

router.beforeEach(async (to, from, next) => {
  const auth = useAuth();
  if (!auth.initialized.value) {
    await auth.restore();
  }
  if (!to.meta.public && !auth.isAuthenticated.value) {
    next({ name: 'login', query: { redirect: to.fullPath } });
    return;
  }
  if (
    to.meta.public &&
    auth.isAuthenticated.value &&
    (to.name === 'login' || to.name === 'register' || to.name === 'register-details')
  ) {
    next({ name: 'search' });
    return;
  }
  next();
});

export default router;
