<template>
  <div class="d-flex">
    <Sidebar class="d-none d-lg-block" />
    <div class="flex-grow-1">
      <Topbar />
      <main class="container-fluid py-4 px-lg-5">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import Sidebar from './Sidebar.vue';
import Topbar from './Topbar.vue';
</script>
