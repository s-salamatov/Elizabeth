<template>
  <div class="auth-shell">
    <div class="container auth-card">
      <div class="card shadow-lg">
        <div class="card-body p-4 p-md-5">
          <div class="text-center mb-4">
            <div class="pill-group mb-2">Регистрация · шаг {{ step }}</div>
            <h1 class="fw-bold mb-1">Создать аккаунт</h1>
            <p class="text-muted mb-0">
              Сначала укажите email и пароль, затем заполните контактные данные.
            </p>
          </div>

          <form v-if="step === 1" class="row g-3" @submit.prevent="handleStepOne">
            <div class="col-12">
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
              <div class="form-text" :class="{ 'text-danger': passwordWeak, 'text-success': !passwordWeak }">
                {{ passwordHint }}
              </div>
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
              <button class="btn btn-gradient" type="submit" :disabled="auth.state.loading || passwordWeak">
                <span v-if="auth.state.loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                <i v-else class="bi bi-arrow-right-circle me-1"></i>
                Продолжить
              </button>
              <RouterLink to="/login" class="text-decoration-none">У меня уже есть аккаунт</RouterLink>
            </div>
            <AlertMessage v-if="auth.state.error" :message="auth.state.error" variant="danger" class="mt-2" />
          </form>

          <form v-else class="row g-3" @submit.prevent="handleStepTwo">
            <div class="col-md-6">
              <label class="form-label w-100" for="register-phone">
                Телефон
                <input
                  id="register-phone"
                  name="phone"
                  v-model="phoneNumber"
                  class="form-control"
                  autocomplete="tel"
                  required
                  placeholder="+79001234567"
                />
              </label>
            </div>
            <div class="col-md-6">
              <label class="form-label w-100" for="register-country">
                Страна
                <select
                  id="register-country"
                  name="country"
                  v-model="country"
                  class="form-select"
                  required
                >
                  <option v-for="option in countryOptions" :key="option.value" :value="option.value">
                    {{ option.emoji }} {{ option.label }}
                  </option>
                </select>
              </label>
            </div>
            <div class="col-md-6">
              <label class="form-label w-100" for="register-first-name">
                Имя
                <input
                  id="register-first-name"
                  name="first_name"
                  v-model="firstName"
                  class="form-control"
                  autocomplete="given-name"
                  placeholder="Иван"
                />
              </label>
            </div>
            <div class="col-md-6">
              <label class="form-label w-100" for="register-last-name">
                Фамилия
                <input
                  id="register-last-name"
                  name="last_name"
                  v-model="lastName"
                  class="form-control"
                  autocomplete="family-name"
                  placeholder="Иванов"
                />
              </label>
            </div>
            <div class="col-md-6">
              <label class="form-label w-100" for="register-tz">
                Часовой пояс
                <select
                  id="register-tz"
                  name="timezone"
                  v-model="defaultTz"
                  class="form-select"
                  required
                >
                  <option v-for="tz in timezoneOptions" :key="tz.value" :value="tz.value">
                    {{ tz.label }}
                  </option>
                </select>
              </label>
              <div class="form-text">Хранится в браузере, по умолчанию — время браузера.</div>
            </div>
            <div class="col-12 d-flex flex-wrap gap-3 align-items-center mt-2">
              <button class="btn btn-gradient" type="submit" :disabled="auth.state.loading">
                <span v-if="auth.state.loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                <i v-else class="bi bi-check2-circle me-1"></i>
                Завершить регистрацию
              </button>
              <RouterLink to="/login" class="text-decoration-none">У меня уже есть аккаунт</RouterLink>
            </div>
            <AlertMessage
              v-if="auth.state.error"
              :message="phoneError || auth.state.error"
              variant="danger"
              class="mt-2"
            />
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuth } from '../stores/useAuth';
import AlertMessage from '../components/common/AlertMessage.vue';

const auth = useAuth();
const router = useRouter();
const route = useRoute();

const step = ref(route.name === 'register-details' ? 2 : 1);
const email = ref('');
const password = ref('');
const password2 = ref('');
const phoneNumber = ref('');
const firstName = ref('');
const lastName = ref('');
const country = ref('RU');
const defaultTz = ref(localStorage.getItem('elizabeth_timezone') || 'browser');

const countryOptions = [
  { value: 'RU', label: 'Россия', emoji: '🇷🇺' },
  { value: 'KZ', label: 'Казахстан', emoji: '🇰🇿' },
  { value: 'BY', label: 'Беларусь', emoji: '🇧🇾' },
];

const timezoneOptions = [
  { value: 'browser', label: 'Время браузера (рекомендуется)' },
  { value: 'Europe/Moscow', label: 'Europe/Moscow' },
  { value: 'Asia/Almaty', label: 'Asia/Almaty' },
  { value: 'Europe/Minsk', label: 'Europe/Minsk' },
  { value: 'UTC', label: 'UTC' },
];

const passwordWeak = computed(() => {
  const value = password.value;
  const hasLength = value.length >= 8;
  const hasNumber = /\d/.test(value);
  const hasLetter = /[A-Za-z]/.test(value);
  return !(hasLength && hasNumber && hasLetter);
});

const passwordHint = computed(() =>
  passwordWeak.value
    ? 'Пароль слабый: добавьте буквы и цифры, минимум 8 символов.'
    : 'Пароль выглядит достаточно надежным.',
);

watch(
  () => route.name,
  (name) => {
    step.value = name === 'register-details' ? 2 : 1;
  },
);

const handleStepOne = async () => {
  if (password.value !== password2.value) {
    auth.state.error = 'Пароли не совпадают';
    return;
  }
  if (passwordWeak.value) {
    auth.state.error = 'Пароль слишком простой';
    return;
  }
  auth.state.error = null;
  step.value = 2;
  router.push({ name: 'register-details' });
};

const handleStepTwo = async () => {
  auth.state.error = null;
  const success = await auth.register({
    email: email.value.trim(),
    password: password.value,
    phone_number: phoneNumber.value,
    first_name: firstName.value,
    last_name: lastName.value,
    country: country.value,
    timezone: defaultTz.value,
  });
  if (success) {
    localStorage.setItem('elizabeth_timezone', defaultTz.value);
    router.push('/search');
  }
};

const phoneError = computed(() =>
  auth.state.error && auth.state.error.toLowerCase().includes('телефон')
    ? auth.state.error
    : '',
);
</script>
