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
            <small class="text-muted d-none d-sm-block">Работаем с каталогом Armtek</small>
          </div>
        </div>
        <div class="d-none d-md-flex align-items-center gap-2 text-muted small">
          <span class="pill-group">REST /api/v1</span>
          <span>Сессия активна</span>
        </div>
      </div>
      <div class="d-flex align-items-center gap-2 flex-wrap justify-content-end">
        <div class="topbar-user" v-if="auth.state.user">
          <i class="bi bi-person-circle text-primary"></i>
          <div class="small lh-sm">
            <div class="fw-semibold">
              {{ auth.state.user.first_name || auth.state.user.email }}
            </div>
            <span class="text-muted">{{ auth.state.user.email }}</span>
          </div>
        </div>
        <ThemeToggle />
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
