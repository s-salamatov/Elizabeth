<template>
  <div class="auth-shell">
    <div class="container auth-card">
      <div class="card shadow-lg">
        <div class="card-body p-4 p-md-5">
          <div class="text-center mb-4">
            <div class="pill-group mb-2">SPA • Armtek</div>
            <h1 class="fw-bold mb-1">Elizabeth</h1>
            <p class="text-muted mb-0">Современная панель для поиска, проверки наличия и загрузки характеристик.</p>
          </div>

          <div class="mb-3 text-start">
            <h5 class="card-title mb-1">Войти в систему</h5>
            <p class="text-muted mb-0">Введите учётные данные Django. Токен хранится только в браузере и не передается третьим лицам.</p>
          </div>

          <form class="d-flex flex-column gap-3" @submit.prevent="submit">
            <div>
              <label class="form-label w-100" for="login-username">
                Логин
                <input
                  id="login-username"
                  name="username"
                  v-model="username"
                  class="form-control"
                  autocomplete="username"
                  required
                  placeholder="Введите логин"
                />
              </label>
            </div>
            <div>
              <label class="form-label w-100" for="login-password">
                Пароль
                <input
                  id="login-password"
                  name="password"
                  v-model="password"
                  type="password"
                  class="form-control"
                  autocomplete="current-password"
                  required
                  placeholder="Введите пароль"
                />
              </label>
              <div class="form-text">Используйте логин и пароль Django-учётной записи. При ошибке проверим текст и предложим повторить.</div>
            </div>
            <button class="btn btn-gradient w-100 d-inline-flex align-items-center justify-content-center" type="submit" :disabled="auth.state.loading">
              <span v-if="auth.state.loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
              <i v-else class="bi bi-box-arrow-in-right me-2"></i>
              Войти в аккаунт
            </button>
            <AlertMessage
              v-if="auth.state.error"
              :message="auth.state.error"
              variant="danger"
            />
          </form>

          <p class="mt-4 mb-0 text-muted text-center small">
            Используйте логин и пароль Django-учётной записи. Токен хранится только в браузере.
          </p>
          <p class="mt-2 mb-0 text-muted text-center">
            Нет аккаунта?
            <RouterLink to="/register">Зарегистрируйтесь</RouterLink>.
          </p>
        </div>
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
