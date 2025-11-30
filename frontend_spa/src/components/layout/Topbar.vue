<template>
  <header class="d-flex align-items-center justify-content-between px-3 px-lg-5 py-3 border-bottom border-dark-subtle">
    <div>
      <div class="d-flex align-items-center gap-2">
        <span class="badge rounded-pill bg-primary bg-opacity-25 text-primary fw-semibold">REST API</span>
        <small class="text-muted">Работаем через /api/v1 без лишних костылей</small>
      </div>
    </div>
    <div class="d-flex align-items-center gap-3">
      <ThemeToggle />
      <div class="text-end d-none d-md-block" v-if="auth.state.user">
        <div class="fw-semibold">{{ auth.state.user.username }}</div>
        <small class="text-muted">в системе</small>
      </div>
      <button class="btn btn-outline-light btn-sm" @click="logout">
        <i class="bi bi-box-arrow-right me-1"></i>
        Выйти
      </button>
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
