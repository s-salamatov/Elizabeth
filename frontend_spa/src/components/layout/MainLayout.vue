<template>
  <div class="app-frame">
    <Topbar />
    <nav class="subnav d-lg-none">
      <div class="container page-container d-flex align-items-center">
        <RouterLink class="nav-link" :class="{ active: route.name === 'search' }" to="/search">Поиск</RouterLink>
        <RouterLink class="nav-link" :class="{ active: route.name === 'requests' }" to="/requests">Запросы</RouterLink>
        <RouterLink class="nav-link" :class="{ active: route.name === 'settings' }" to="/settings">Настройки</RouterLink>
      </div>
    </nav>
    <div class="d-flex">
      <Sidebar class="d-none d-lg-block" />
      <div class="flex-grow-1">
        <main class="page-container main-shell">
          <slot />
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router';
import Sidebar from './Sidebar.vue';
import Topbar from './Topbar.vue';

const route = useRoute();
</script>
