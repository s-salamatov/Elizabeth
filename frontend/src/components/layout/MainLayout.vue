<template>
  <div class="app-shell">
    <Topbar />
    <nav class="section-nav">
      <div class="container page-container d-flex align-items-center">
        <RouterLink class="nav-link" :class="{ active: route.name === 'search' }" to="/search">Поиск товаров</RouterLink>
        <RouterLink class="nav-link" :class="{ active: route.name === 'requests' }" to="/requests">Мои запросы</RouterLink>
        <RouterLink class="nav-link" :class="{ active: route.name === 'settings' }" to="/settings">Настройки</RouterLink>
      </div>
    </nav>
    <main class="page-container main-shell">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router';
import Topbar from './Topbar.vue';

const route = useRoute();
</script>
