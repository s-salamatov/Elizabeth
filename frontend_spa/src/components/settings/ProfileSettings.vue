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
          <label class="form-label" for="profile-source">
            Источник поиска
            <select id="profile-source" name="defaultSource" class="form-select" v-model="defaultSource">
              <option value="armtek">Armtek (рекомендовано)</option>
              <option value="catalog">Внутренний каталог</option>
            </select>
          </label>
          <div class="form-text">По умолчанию backend настроен на Armtek. Другие источники появятся позже.</div>
        </div>
        <div class="col-md-6">
          <label class="form-label" for="profile-timezone">
            Часовой пояс (локально)
            <select id="profile-timezone" name="timezone" class="form-select" v-model="timezone">
              <option value="Europe/Moscow">Europe/Moscow</option>
              <option value="Europe/Minsk">Europe/Minsk</option>
              <option value="Europe/Riga">Europe/Riga</option>
              <option value="UTC">UTC</option>
            </select>
          </label>
          <div class="form-text">Параметр хранится в браузере и помогает форматировать даты.</div>
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
          <button class="btn btn-gradient" type="submit" :disabled="saving">
            <i class="bi bi-save me-1"></i>
            Сохранить настройки
          </button>
          <span class="text-muted" v-if="saving">Сохраняем профиль…</span>
        </div>
        <div class="col-12">
          <div class="form-text">Тема и часовой пояс применяются только на этом устройстве и в этом браузере.</div>
        </div>
        <AlertMessage v-if="message" :message="message" :variant="messageVariant" />
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useAuth } from '../../stores/useAuth';
import { useTheme } from '../../stores/useTheme';
import AlertMessage from '../common/AlertMessage.vue';

const auth = useAuth();
const email = ref('');
const defaultSource = ref('armtek');
const timezone = ref(localStorage.getItem('elizabeth_timezone') || 'Europe/Moscow');
const saving = ref(false);
const message = ref('');
const messageVariant = ref('info');
const theme = useTheme();

const loadInitial = () => {
  if (auth.state.user) {
    email.value = auth.state.user.email || '';
  }
  if (auth.state.settings?.default_search_source) {
    defaultSource.value = auth.state.settings.default_search_source;
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
    default_search_source: defaultSource.value,
  });
  saving.value = false;
  if (success) {
    localStorage.setItem('elizabeth_timezone', timezone.value);
    messageVariant.value = 'success';
    message.value = 'Настройки сохранены. Тема и часовой пояс применены в браузере.';
  } else {
    messageVariant.value = 'danger';
    message.value = auth.state.error || 'Не удалось сохранить настройки.';
  }
};
</script>
