<template>
  <MainLayout>
    <div class="page-header">
      <h1>Настройки</h1>
      <p class="text-muted">Управляйте профилем, темой и учётными данными поставщиков. Все API-запросы идут по /api/v1.</p>
    </div>

    <div class="card">
      <div class="card-header bg-transparent">
        <div class="nav nav-pills gap-2">
          <button class="btn btn-ghost" :class="{ active: activeTab === 'profile' }" @click="activeTab = 'profile'">
            <i class="bi bi-person-gear me-1"></i> Профиль
          </button>
          <button class="btn btn-ghost" :class="{ active: activeTab === 'providers' }" @click="activeTab = 'providers'">
            <i class="bi bi-diagram-3 me-1"></i> Провайдеры
          </button>
        </div>
      </div>
      <div class="card-body">
        <ProfileSettings v-if="activeTab === 'profile'" />
        <ProviderSettings v-else />
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
