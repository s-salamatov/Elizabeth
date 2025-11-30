<template>
  <div class="card">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-start flex-wrap gap-2 mb-3">
        <div>
          <h5 class="card-title mb-1">Провайдеры данных</h5>
          <p class="text-muted mb-0">Добавьте учетные данные Armtek, чтобы искать товары и получать характеристики.</p>
        </div>
        <span class="badge-soft">Armtek</span>
      </div>
      <div class="row g-3">
        <div class="col-md-6">
          <label class="form-label">Логин</label>
          <input v-model="login" class="form-control" placeholder="Ваш Armtek логин" />
        </div>
        <div class="col-md-6">
          <label class="form-label">Пароль</label>
          <input v-model="password" type="password" class="form-control" placeholder="••••••••" />
        </div>
      </div>
      <div class="form-text mt-2">
        Храним пароль в зашифрованном виде. При ошибке авторизации покажем подсказку ниже.
      </div>
      <div class="d-flex gap-2 mt-3">
        <button class="btn btn-gradient" :disabled="saving" @click="save">
          <i class="bi bi-shield-lock me-1"></i>
          Сохранить аккаунт Armtek
        </button>
        <button class="btn btn-outline-danger" type="button" :disabled="!hasExisting || saving" @click="remove">
          <i class="bi bi-trash me-1"></i>
          Удалить
        </button>
      </div>
      <AlertMessage v-if="message" :message="message" :variant="messageVariant" class="mt-3" />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { ProviderApi } from '../../api';
import AlertMessage from '../common/AlertMessage.vue';

const login = ref('');
const password = ref('');
const saving = ref(false);
const hasExisting = ref(false);
const message = ref('');
const messageVariant = ref('info');

const loadCredentials = async () => {
  try {
    const { status, data } = await ProviderApi.armtekCredentials();
    if (status === 200 && data?.login) {
      login.value = data.login;
      hasExisting.value = true;
    } else {
      hasExisting.value = false;
    }
  } catch (error) {
    hasExisting.value = false;
  }
};

onMounted(() => {
  loadCredentials();
});

const save = async () => {
  saving.value = true;
  message.value = '';
  try {
    await ProviderApi.saveArmtek({ login: login.value, password: password.value });
    message.value = 'Учётные данные сохранены. Теперь можно запускать поиск и загрузку характеристик.';
    messageVariant.value = 'success';
    hasExisting.value = true;
    password.value = '';
  } catch (error) {
    message.value =
      error.response?.data?.detail || 'Не удалось подключиться к Armtek. Проверьте логин/пароль.';
    messageVariant.value = 'danger';
  } finally {
    saving.value = false;
  }
};

const remove = async () => {
  saving.value = true;
  message.value = '';
  try {
    await ProviderApi.deleteArmtek();
    message.value = 'Данные Armtek удалены. Добавьте новые, чтобы продолжить пользоваться поиском.';
    messageVariant.value = 'warning';
    hasExisting.value = false;
    login.value = '';
    password.value = '';
  } catch (error) {
    message.value = 'Не удалось удалить данные. Попробуйте ещё раз.';
    messageVariant.value = 'danger';
  } finally {
    saving.value = false;
  }
};
</script>
