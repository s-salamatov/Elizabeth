<template>
  <header class="topbar">
    <div class="container page-container d-flex align-items-center justify-content-between py-3">
      <div class="d-flex align-items-center gap-3">
        <div class="brand d-flex align-items-center gap-2">
          <i class="bi bi-search text-primary"></i>
          <span>Elizabeth</span>
        </div>
        <div class="d-none d-md-flex align-items-center gap-2 text-muted small">
          <span class="pill-group">REST API</span>
          <span>Работаем через /api/v1</span>
        </div>
      </div>
      <div class="d-flex align-items-center gap-3">
        <ThemeToggle />
        <div class="text-end d-none d-md-block" v-if="auth.state.user">
          <div class="fw-semibold">{{ auth.state.user.username }}</div>
          <small class="text-muted">в системе</small>
        </div>
        <button class="btn btn-ghost btn-sm" @click="logout">
          <i class="bi bi-box-arrow-right me-1"></i>
          Выйти
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useAuth } from '../../stores/useAuth';
import ThemeToggle from '../common/ThemeToggle.vue';

const auth = useAuth();
const router = useRouter();

const logout = () => {
  auth.logout();
  router.push({ name: 'login' });
};
</script>
