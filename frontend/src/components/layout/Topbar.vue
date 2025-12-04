<template>
  <header class="topbar">
    <div class="container page-container d-flex align-items-center justify-content-between py-3 gap-3 topbar-grid">
      <div class="d-flex align-items-center gap-3 flex-wrap">
        <div class="brand d-flex align-items-center gap-2">
          <div class="brand-mark">
            <span>El</span>
          </div>
          <div>
            <div>Elizabeth</div>
          </div>
        </div>
        <div class="d-none d-md-flex align-items-center gap-2 text-muted small live-status">
          <span class="status-dot blink"></span>
          <span class="fw-semibold">Системы доступны</span>
        </div>
        <nav class="topbar-nav d-none d-md-flex">
          <RouterLink class="nav-link" :class="{ active: route.name === 'search' }" to="/search">
            <i class="bi bi-search"></i> Поиск
          </RouterLink>
          <RouterLink class="nav-link" :class="{ active: route.name === 'requests' }" to="/requests">
            <i class="bi bi-clock-history"></i> Запросы
          </RouterLink>
        </nav>
      </div>
      <div class="d-flex align-items-center gap-2 flex-wrap justify-content-end">
        <div class="dropdown" v-if="auth.state.user">
          <button
            class="btn btn-ghost btn-sm dropdown-toggle d-inline-flex align-items-center gap-2"
            type="button"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            <i class="bi bi-person-circle text-primary"></i>
            <div class="small lh-sm text-start">
              <div class="fw-semibold">{{ displayName }}</div>
              <span class="text-muted">{{ auth.state.user.email }}</span>
            </div>
          </button>
          <ul class="dropdown-menu dropdown-menu-end shadow-sm">
            <li class="dropdown-header">Аккаунт</li>
            <li>
              <RouterLink class="dropdown-item d-flex align-items-center gap-2" to="/settings">
                <i class="bi bi-gear"></i>
                Настройки профиля
              </RouterLink>
            </li>
            <li><hr class="dropdown-divider" /></li>
            <li class="dropdown-header d-flex align-items-center gap-2">
              <i class="bi bi-circle-half"></i>
              Тема
            </li>
            <li class="px-3 py-2">
              <div class="btn-group w-100" role="group">
                <button type="button" class="btn btn-outline-light btn-sm" :class="{ active: theme.theme.value === 'system' }" @click="theme.setTheme('system')">Система</button>
                <button type="button" class="btn btn-outline-light btn-sm" :class="{ active: theme.theme.value === 'light' }" @click="theme.setTheme('light')">Светлая</button>
                <button type="button" class="btn btn-outline-light btn-sm" :class="{ active: theme.theme.value === 'dark' }" @click="theme.setTheme('dark')">Тёмная</button>
              </div>
            </li>
            <li><hr class="dropdown-divider" /></li>
            <li>
              <button class="dropdown-item d-flex align-items-center gap-2" type="button" @click="logout">
                <i class="bi bi-box-arrow-right"></i>
                Выйти
              </button>
            </li>
          </ul>
        </div>
        <ThemeToggle />
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '../../stores/useAuth';
import { useTheme } from '../../stores/useTheme';
import { useRoute } from 'vue-router';

const auth = useAuth();
const router = useRouter();
const theme = useTheme();
const route = useRoute();

const displayName = computed(() => {
  const first = auth.state.user.first_name || '';
  const last = auth.state.user.last_name || '';
  const full = `${first} ${last}`.trim();
  return full || auth.state.user.email || 'Аккаунт';
});

const logout = () => {
  auth.logout();
  router.push({ name: 'login' });
};
</script>

<style scoped>
.brand-mark {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: linear-gradient(140deg, var(--color-primary), var(--color-accent));
  color: #0f172a;
  display: grid;
  place-items: center;
  font-weight: 800;
  letter-spacing: -0.02em;
  box-shadow: 0 10px 24px rgba(111, 143, 255, 0.35);
}

.live-status .status-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #22c55e;
  box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.45);
}

.live-status .blink {
  animation: pulse 1.6s ease-in-out infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.45); }
  70% { box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
  100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
}

.topbar-grid { gap: 1rem; }
.topbar-nav {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
}
.topbar-nav .nav-link {
  color: var(--color-muted);
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.5rem;
  border-radius: 999px;
  transition: color var(--transition-base), background-color var(--transition-base);
}
.topbar-nav .nav-link.active,
.topbar-nav .nav-link.router-link-active {
  color: var(--color-text);
  background: rgba(111, 143, 255, 0.12);
}
</style>
