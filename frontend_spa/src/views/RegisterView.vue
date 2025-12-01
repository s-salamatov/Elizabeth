<template>
  <div class="container py-5" style="max-width: 640px;">
    <div class="text-center mb-4">
      <h1 class="fw-bold">Создать аккаунт</h1>
      <p class="text-muted">Регистрация в один шаг. После создания мы сразу авторизуем вас и откроем рабочую панель.</p>
    </div>
    <div class="card">
      <div class="card-body">
        <h5 class="card-title">Регистрация</h5>
        <form @submit.prevent="submit">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label" for="register-username">
                Логин
                <input
                  id="register-username"
                  name="username"
                  v-model="username"
                  class="form-control"
                  autocomplete="username"
                  required
                />
              </label>
              <div class="form-text">Минимум 3 символа. Используется для входа.</div>
            </div>
            <div class="col-md-6">
              <label class="form-label" for="register-email">
                Email
                <input
                  id="register-email"
                  name="email"
                  v-model="email"
                  type="email"
                  class="form-control"
                  autocomplete="email"
                  required
                />
              </label>
            </div>
            <div class="col-md-6">
              <label class="form-label" for="register-password">
                Пароль
                <input
                  id="register-password"
                  name="password"
                  v-model="password"
                  type="password"
                  class="form-control"
                  autocomplete="new-password"
                  required
                />
              </label>
            </div>
            <div class="col-md-6">
              <label class="form-label" for="register-password2">
                Повтор пароля
                <input
                  id="register-password2"
                  name="password-confirmation"
                  v-model="password2"
                  type="password"
                  class="form-control"
                  autocomplete="new-password"
                  required
                />
              </label>
            </div>
          </div>
          <div class="d-flex align-items-center gap-3 mt-4">
            <button class="btn btn-gradient" type="submit" :disabled="auth.state.loading">
              <i class="bi bi-person-check me-1"></i>
              Создать аккаунт
            </button>
            <RouterLink to="/login" class="text-light">У меня уже есть аккаунт</RouterLink>
          </div>
          <AlertMessage v-if="auth.state.error" :message="auth.state.error" variant="danger" class="mt-3" />
        </form>
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
