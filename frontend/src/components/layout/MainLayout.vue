<template>
  <div class="app-shell">
    <Topbar />
    <main class="page-container main-shell">
      <slot />
    </main>
  </div>
</template>

<script setup>
import Topbar from './Topbar.vue';
</script>
