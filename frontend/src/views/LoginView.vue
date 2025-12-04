<template>
  <div class="auth-shell">
    <div class="container auth-card">
      <div class="card shadow-lg">
        <div class="card-body p-4 p-md-5">
          <div class="text-center mb-4">
            <div class="pill-group mb-2">Elizabeth</div>
            <h1 class="fw-bold mb-1">Войти</h1>
          </div>

          <form class="d-flex flex-column gap-3" @submit.prevent="submit">
            <div>
              <label class="form-label w-100" for="login-email">
                <input
                  id="login-email"
                  name="email"
                  type="email"
                  v-model="email"
                  class="form-control"
                  autocomplete="email"
                  required
                  placeholder="Email"
                />
              </label>
            </div>
            <div>
              <label class="form-label w-100" for="login-password">
                <input
                  id="login-password"
                  name="password"
                  v-model="password"
                  type="password"
                  class="form-control"
                  autocomplete="current-password"
                  required
                  placeholder="Пароль"
                />
              </label>
            </div>
            <button class="btn btn-gradient w-100 d-inline-flex align-items-center justify-content-center" type="submit" :disabled="auth.state.loading">
              <span v-if="auth.state.loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
              <i v-else class="bi bi-box-arrow-in-right me-2"></i>
              Войти
            </button>
            <AlertMessage
              v-if="auth.state.error"
              :message="auth.state.error"
              variant="danger"
            />
          </form>

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

const email = ref('');
const password = ref('');
const router = useRouter();
const route = useRoute();
const auth = useAuth();

const submit = async () => {
  const success = await auth.login({ email: email.value, password: password.value });
  if (success) {
    const redirect = route.query.redirect || '/search';
    router.push(redirect);
  }
};
</script>
