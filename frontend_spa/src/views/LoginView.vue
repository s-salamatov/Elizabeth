<template>
  <div class="container py-5" style="max-width: 560px;">
    <div class="text-center mb-4">
      <h1 class="fw-bold">Elizabeth</h1>
      <p class="text-muted">SPA-интерфейс для работы с поиском Armtek. Войдите, чтобы продолжить.</p>
    </div>
    <div class="card">
      <div class="card-body">
        <h5 class="card-title">Вход</h5>
        <p class="text-muted">Используйте логин и пароль вашей Django-учётки. Токен хранится только в браузере.</p>
        <form @submit.prevent="submit">
          <div class="mb-3">
            <label class="form-label" for="login-username">
              Логин
              <input
                id="login-username"
                name="username"
                v-model="username"
                class="form-control"
                autocomplete="username"
                required
              />
            </label>
          </div>
          <div class="mb-3">
            <label class="form-label" for="login-password">
              Пароль
              <input
                id="login-password"
                name="password"
                v-model="password"
                type="password"
                class="form-control"
                autocomplete="current-password"
                required
              />
            </label>
            <div class="form-text">Токен формируется через /api/v1/auth/login.</div>
          </div>
          <button class="btn btn-gradient w-100" type="submit" :disabled="auth.state.loading">
            <i class="bi bi-box-arrow-in-right me-1"></i>
            Войти в аккаунт
          </button>
          <AlertMessage v-if="auth.state.error" :message="auth.state.error" variant="danger" class="mt-3" />
        </form>
        <p class="mt-3 mb-0 text-muted">Нет аккаунта? <RouterLink to="/register">Зарегистрируйтесь</RouterLink>.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuth } from '../stores/useAuth';
import AlertMessage from '../components/common/AlertMessage.vue';

const username = ref('');
const password = ref('');
const router = useRouter();
const route = useRoute();
const auth = useAuth();

const submit = async () => {
  const success = await auth.login({ username: username.value, password: password.value });
  if (success) {
    const redirect = route.query.redirect || '/search';
    router.push(redirect);
  }
};
</script>
