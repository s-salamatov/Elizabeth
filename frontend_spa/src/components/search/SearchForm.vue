<template>
  <div class="card mb-3">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-start mb-2 flex-wrap gap-2">
        <div>
          <h5 class="card-title mb-1">Поиск товаров</h5>
          <p class="text-muted mb-0">Введите артикулами и брендами. Можно сразу несколько строк, разделённых запятыми, точкой с запятой или переносом строк.</p>
        </div>
        <div class="text-end">
          <button class="btn btn-link text-decoration-none text-light" @click="reset" type="button">
            <i class="bi bi-eraser me-1"></i> Очистить поле
          </button>
        </div>
      </div>
      <div class="mb-3">
        <label class="form-label fw-semibold" for="omni-input">
          Артикулы и бренды
          <textarea
            id="omni-input"
            name="omni-input"
            class="form-control"
            rows="5"
            v-model="innerValue"
            placeholder="332101_KYB\n1600332 KYB\nМожно вставить сразу несколько строк"
          ></textarea>
        </label>
        <div class="form-text">
          Пример: 332101_KYB или 1600332 KYB. Разделители: запятая, точка с запятой, перенос строки.
        </div>
      </div>
      <div class="d-flex flex-wrap gap-2">
        <button class="btn btn-gradient" :disabled="loading" @click="emitSearch">
          <i class="bi bi-search me-1"></i>
          Найти товары по артикулам
        </button>
        <button class="btn btn-outline-gradient" type="button" @click="emitSearch(true)" :disabled="loading">
          <i class="bi bi-lightning me-1"></i>
          Быстрый поиск (без очистки)
        </button>
      </div>
      <AlertMessage v-if="error" :message="error" variant="danger" class="mt-3" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import AlertMessage from '../common/AlertMessage.vue';

const props = defineProps({
  modelValue: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
});

const emit = defineEmits(['update:modelValue', 'submit']);
const innerValue = ref(props.modelValue);

watch(
  () => props.modelValue,
  (val) => {
    innerValue.value = val;
  },
);

const emitSearch = (preserve) => {
  emit('submit', { value: innerValue.value, preserve });
};

const reset = () => {
  innerValue.value = '';
  emit('update:modelValue', '');
};

watch(
  innerValue,
  (val) => emit('update:modelValue', val),
);
</script>
