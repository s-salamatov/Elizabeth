<template>
  <MainLayout>
    <div class="row g-3">
      <div class="col-12">
        <div class="hero-intro d-flex justify-content-between align-items-center flex-wrap gap-2">
          <div>
            <h2 class="mb-1">Настройки</h2>
            <p class="text-muted mb-0">Управляйте профилем и поставщиками данных. Все API-запросы идут по /api/v1.</p>
          </div>
          <span class="badge bg-primary">Подсказки встроены прямо в формы</span>
        </div>
      </div>
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <ul class="nav nav-pills card-header-pills">
              <li class="nav-item">
                <button class="nav-link" :class="{ active: activeTab === 'profile' }" @click="activeTab = 'profile'">
                  Профиль
                </button>
              </li>
              <li class="nav-item">
                <button class="nav-link" :class="{ active: activeTab === 'providers' }" @click="activeTab = 'providers'">
                  Провайдеры
                </button>
              </li>
            </ul>
          </div>
          <div class="card-body">
            <ProfileSettings v-if="activeTab === 'profile'" />
            <ProviderSettings v-else />
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup>
import { ref } from 'vue';
import MainLayout from '../components/layout/MainLayout.vue';
import ProfileSettings from '../components/settings/ProfileSettings.vue';
import ProviderSettings from '../components/settings/ProviderSettings.vue';

const activeTab = ref('profile');
</script>
