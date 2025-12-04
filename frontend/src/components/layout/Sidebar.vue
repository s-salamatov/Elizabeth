<template>
  <nav class="sidebar p-4">
    <div class="d-flex align-items-center gap-2 mb-4">
      <div class="p-2 bg-primary bg-opacity-25 rounded-3">
        <i class="bi bi-search text-primary"></i>
      </div>
      <div>
        <h5 class="mb-0">Elizabeth</h5>
      </div>
    </div>
    <div class="list-group list-group-flush">
      <RouterLink class="nav-link px-3 py-2" :class="{ active: route.name === 'search' }" to="/search">
        <i class="bi bi-lightning-charge me-2"></i> Поиск товаров
      </RouterLink>
      <RouterLink class="nav-link px-3 py-2" :class="{ active: route.name === 'requests' }" to="/requests">
        <i class="bi bi-clock-history me-2"></i> Мои запросы
      </RouterLink>
      <RouterLink class="nav-link px-3 py-2" :class="{ active: route.name === 'settings' }" to="/settings">
        <i class="bi bi-gear-wide-connected me-2"></i> Настройки
      </RouterLink>
    </div>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router';

const route = useRoute();
</script>
