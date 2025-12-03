<template>
  <div class="card mb-3">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-start flex-wrap gap-2 mb-3">
        <div>
          <h5 class="card-title mb-1">Профиль</h5>
          <p class="text-muted mb-0">Обновите контактные данные, источник поиска и тему, чтобы интерфейс подстраивался под ваш рабочий режим.</p>
        </div>
        <span class="badge-soft">Сохраняется на сервере</span>
      </div>
      <form class="row g-3" @submit.prevent="saveProfile">
        <div class="col-md-6">
          <label class="form-label" for="profile-email">
            Email
            <input
              id="profile-email"
              name="email"
              type="email"
              class="form-control"
              v-model="email"
              placeholder="user@example.com"
            />
          </label>
          <div class="form-text">Используем для уведомлений и восстановления доступа.</div>
        </div>
        <div class="col-md-6">
          <label class="form-label" for="profile-phone">
            Телефон
            <input
              id="profile-phone"
              name="phone_number"
              type="tel"
              class="form-control"
              v-model="phoneNumber"
              required
              placeholder="+79001234567"
            />
          </label>
        </div>
        <div class="col-md-6">
          <label class="form-label" for="profile-first-name">
            Имя
            <input
              id="profile-first-name"
              name="first_name"
              class="form-control"
              v-model="firstName"
              placeholder="Иван"
            />
          </label>
        </div>
        <div class="col-md-6">
          <label class="form-label" for="profile-last-name">
            Фамилия
            <input
              id="profile-last-name"
              name="last_name"
              class="form-control"
              v-model="lastName"
              placeholder="Иванов"
            />
          </label>
        </div>
        <div class="col-md-6">
          <label class="form-label" for="profile-country">
            Страна
            <select id="profile-country" name="country" class="form-select" v-model="country" required>
              <option v-for="option in countryOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>
        </div>
        <div class="col-md-6">
          <label class="form-label" for="profile-source">
            Источник поиска
            <select id="profile-source" name="defaultSource" class="form-select" v-model="defaultSource">
              <option value="armtek">Armtek (рекомендовано)</option>
              <option value="catalog">Внутренний каталог</option>
            </select>
          </label>
          <div class="form-text">По умолчанию backend настроен на Armtek.</div>
        </div>
        <div class="col-md-6">
          <label class="form-label" for="profile-timezone">
            Часовой пояс
            <select id="profile-timezone" name="timezone" class="form-select" v-model="timezone">
              <option value="browser">Время браузера (рекомендуется)</option>
              <option value="Europe/Moscow">Europe/Moscow</option>
              <option value="Asia/Almaty">Asia/Almaty</option>
              <option value="Europe/Minsk">Europe/Minsk</option>
              <option value="UTC">UTC</option>
            </select>
          </label>
          <div class="form-text">Хранится в браузере и влияет на форматирование дат.</div>
        </div>
        <div class="col-md-6">
          <p class="form-label mb-1">Тема оформления</p>
          <div class="d-flex gap-2 flex-wrap">
            <span class="theme-chip" :class="{ 'bg-dark text-white': theme.resolvedTheme.value === 'dark' }">
              <i class="bi" :class="themeIcon"></i>
              {{ themeLabel }}
            </span>
            <div class="btn-group" role="group">
              <button type="button" class="btn btn-outline-light" :class="{ active: theme.theme.value === 'system' }" @click="theme.setTheme('system')">Системная</button>
              <button type="button" class="btn btn-outline-light" :class="{ active: theme.theme.value === 'light' }" @click="theme.setTheme('light')">Светлая</button>
              <button type="button" class="btn btn-outline-light" :class="{ active: theme.theme.value === 'dark' }" @click="theme.setTheme('dark')">Тёмная</button>
            </div>
          </div>
          <div class="form-text">Тема применяется сразу и сохраняется в браузере.</div>
        </div>
        <div class="col-12 d-flex align-items-center gap-2">
          <button class="btn btn-gradient" type="submit" :disabled="saving || deleting">
            <i class="bi bi-save me-1"></i>
            Сохранить настройки
          </button>
          <span class="text-muted" v-if="saving">Сохраняем профиль…</span>
        </div>
        <div class="col-12">
          <div class="form-text">Тема сохраняется локально, остальные поля — на сервере.</div>
        </div>
        <div class="col-12">
          <hr class="my-3" />
          <div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-2">
            <div>
              <h6 class="mb-1 text-danger">Удалить аккаунт</h6>
              <p class="text-muted mb-0">Профиль и связанные данные будут удалены без возможности восстановления.</p>
            </div>
            <button class="btn btn-outline-danger" type="button" :disabled="deleting" @click="deleteProfile">
              <i class="bi bi-trash me-1"></i>
              {{ deleting ? 'Удаляем…' : 'Удалить аккаунт' }}
            </button>
          </div>
        </div>
        <AlertMessage v-if="message" :message="message" :variant="messageVariant" />
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '../../stores/useAuth';
import { useTheme } from '../../stores/useTheme';
import AlertMessage from '../common/AlertMessage.vue';

const auth = useAuth();
const router = useRouter();
const email = ref('');
const phoneNumber = ref('');
const firstName = ref('');
const lastName = ref('');
const country = ref('RU');
const defaultSource = ref('armtek');
const timezone = ref(localStorage.getItem('elizabeth_timezone') || 'browser');
const saving = ref(false);
const deleting = ref(false);
const message = ref('');
const messageVariant = ref('info');
const theme = useTheme();

const countryOptions = [
  { value: 'RU', label: 'Россия' },
  { value: 'KZ', label: 'Казахстан' },
  { value: 'BY', label: 'Беларусь' },
];

const loadInitial = () => {
  if (auth.state.user) {
    email.value = auth.state.user.email || '';
    phoneNumber.value = auth.state.user.phone_number || '';
    firstName.value = auth.state.user.first_name || '';
    lastName.value = auth.state.user.last_name || '';
  }
  if (auth.state.settings?.default_search_source) {
    defaultSource.value = auth.state.settings.default_search_source;
  }
  if (auth.state.settings?.country) {
    country.value = auth.state.settings.country;
  }
};

onMounted(() => {
  loadInitial();
});

const themeIcon = computed(() =>
  theme.resolvedTheme.value === 'dark' ? 'bi-moon-stars' : 'bi-sun',
);
const themeLabel = computed(() =>
  theme.resolvedTheme.value === 'dark' ? 'Тёмная тема' : 'Светлая тема',
);

const saveProfile = async () => {
  saving.value = true;
  message.value = '';
  const success = await auth.updateProfile({
    email: email.value,
    phone_number: phoneNumber.value,
    first_name: firstName.value,
    last_name: lastName.value,
    country: country.value,
    default_search_source: defaultSource.value,
    timezone: timezone.value,
  });
  saving.value = false;
  if (success) {
    localStorage.setItem('elizabeth_timezone', timezone.value);
    messageVariant.value = 'success';
    message.value = 'Настройки сохранены. Часовой пояс сохранён в браузере.';
  } else {
    messageVariant.value = 'danger';
    message.value = auth.state.error || 'Не удалось сохранить настройки.';
  }
};

const deleteProfile = async () => {
  const confirmed = window.confirm(
    'Удалить аккаунт и все связанные данные? Операцию нельзя отменить.',
  );
  if (!confirmed) return;
  deleting.value = true;
  message.value = '';
  const success = await auth.deleteAccount();
  deleting.value = false;
  if (success) {
    router.push({ name: 'login' });
  } else {
    messageVariant.value = 'danger';
    message.value = auth.state.error || 'Не удалось удалить профиль.';
  }
};
</script>
