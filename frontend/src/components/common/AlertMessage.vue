<template>
  <div v-if="message" :class="['alert', `alert-${variant}`, 'd-flex', 'align-items-center', 'gap-2']">
    <i :class="iconClass"></i>
    <div>{{ message }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  message: { type: String, default: '' },
  variant: { type: String, default: 'info' },
});

const iconClass = computed(() => {
  switch (props.variant) {
    case 'danger':
      return 'bi bi-exclamation-octagon-fill text-danger';
    case 'success':
      return 'bi bi-check-circle-fill text-success';
    case 'warning':
      return 'bi bi-exclamation-triangle-fill text-warning';
    default:
      return 'bi bi-info-circle-fill text-info';
  }
});
</script>
