<template>
  <div class="auth-shell">
    <div class="container auth-card">
      <div class="card shadow-lg">
        <div class="card-body p-4 p-md-5">
          <div class="text-center mb-4">
            <div class="pill-group mb-2">Регистрация</div>
            <h1 class="fw-bold mb-1">Создать аккаунт</h1>
            <p class="text-muted mb-0">Один шаг — и вы сразу попадёте в рабочую панель.</p>
          </div>

          <form class="row g-3" @submit.prevent="submit">
            <div class="col-md-6">
              <label class="form-label w-100" for="register-username">
                Логин
                <input
                  id="register-username"
                  name="username"
                  v-model="username"
                  class="form-control"
                  autocomplete="username"
                  required
                  placeholder="work.user"
                />
              </label>
              <div class="form-text">Минимум 3 символа. Используется для входа.</div>
            </div>
            <div class="col-md-6">
              <label class="form-label w-100" for="register-email">
                Email
                <input
                  id="register-email"
                  name="email"
                  v-model="email"
                  type="email"
                  class="form-control"
                  autocomplete="email"
                  required
                  placeholder="you@example.com"
                />
              </label>
            </div>
            <div class="col-md-6">
              <label class="form-label w-100" for="register-password">
                Пароль
                <input
                  id="register-password"
                  name="password"
                  v-model="password"
                  type="password"
                  class="form-control"
                  autocomplete="new-password"
                  required
                  placeholder="••••••••"
                />
              </label>
            </div>
            <div class="col-md-6">
              <label class="form-label w-100" for="register-password2">
                Повтор пароля
                <input
                  id="register-password2"
                  name="password-confirmation"
                  v-model="password2"
                  type="password"
                  class="form-control"
                  autocomplete="new-password"
                  required
                  placeholder="••••••••"
                />
              </label>
            </div>
            <div class="col-12 d-flex flex-wrap gap-3 align-items-center mt-2">
              <button class="btn btn-gradient" type="submit" :disabled="auth.state.loading">
                <span v-if="auth.state.loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                <i v-else class="bi bi-person-check me-1"></i>
                Создать аккаунт
              </button>
              <RouterLink to="/login" class="text-decoration-none">У меня уже есть аккаунт</RouterLink>
            </div>
            <AlertMessage v-if="auth.state.error" :message="auth.state.error" variant="danger" class="mt-2" />
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '../stores/useAuth';
import AlertMessage from '../components/common/AlertMessage.vue';

const username = ref('');
const email = ref('');
const password = ref('');
const password2 = ref('');
const auth = useAuth();
const router = useRouter();

const submit = async () => {
  if (password.value !== password2.value) {
    auth.state.error = 'Пароли не совпадают';
    return;
  }
  const success = await auth.register({
    username: username.value,
    email: email.value,
    password: password.value,
  });
  if (success) {
    router.push('/search');
  }
};
</script>
