<template>
  <header class="topbar">
    <div class="container page-container d-flex align-items-center justify-content-between py-3 gap-3">
      <div class="d-flex align-items-center gap-3">
        <div class="brand d-flex align-items-center gap-2">
          <div class="p-2 rounded-3 bg-primary bg-opacity-10 text-primary">
            <i class="bi bi-search"></i>
          </div>
          <div>
            <div>Elizabeth</div>
          </div>
        </div>
        <div class="d-none d-md-flex align-items-center gap-2 text-muted small">
          <span class="pill-group">🟢 Все системы доступны</span>
        </div>
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
import ThemeToggle from '../common/ThemeToggle.vue';

const auth = useAuth();
const router = useRouter();

const displayName = computed(
  () => auth.state.user.first_name || auth.state.user.email || 'Аккаунт',
);

const logout = () => {
  auth.logout();
  router.push({ name: 'login' });
};
</script>
