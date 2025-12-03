<template>
  <div class="dropdown">
    <button class="btn btn-ghost btn-sm dropdown-toggle d-inline-flex align-items-center gap-2" type="button" data-bs-toggle="dropdown">
      <i :class="themeIcon"></i>
      <span class="d-none d-sm-inline">Тема</span>
    </button>
    <ul class="dropdown-menu dropdown-menu-end shadow-sm">
      <li>
        <button class="dropdown-item" :class="{ active: theme.value === 'system' }" @click="setTheme('system')">
          <i class="bi bi-circle-half me-2"></i> Системная
        </button>
      </li>
      <li>
        <button class="dropdown-item" :class="{ active: theme.value === 'light' }" @click="setTheme('light')">
          <i class="bi bi-sun me-2"></i> Светлая
        </button>
      </li>
      <li>
        <button class="dropdown-item" :class="{ active: theme.value === 'dark' }" @click="setTheme('dark')">
          <i class="bi bi-moon-stars me-2"></i> Тёмная
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useTheme } from '../../stores/useTheme';

const { theme, resolvedTheme, setTheme } = useTheme();

const themeIcon = computed(() => {
  if (resolvedTheme.value === 'dark') return 'bi bi-moon-stars';
  if (resolvedTheme.value === 'light') return 'bi bi-sun';
  return 'bi bi-circle-half';
});
</script>
