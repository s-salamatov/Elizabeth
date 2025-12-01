<template>
  <div class="card mb-3">
    <div class="card-body">
      <div class="section-card-title mb-3">
        <div>
          <h5 class="card-title mb-1">Поиск товаров</h5>
          <p class="text-muted supporting-text mb-0">Вставьте артикулы и бренды списком. Мы запросим Armtek и подготовим результаты для таблицы ниже.</p>
        </div>
        <div class="d-flex align-items-center gap-2">
          <span class="badge-soft d-none d-md-inline-flex"><i class="bi bi-clock-history me-1"></i>Ответ приходит по мере готовности</span>
          <button class="btn btn-ghost btn-link btn-sm" @click="reset" type="button">
            <i class="bi bi-eraser me-1"></i> Очистить поле
          </button>
        </div>
      </div>

      <div class="mb-3">
        <label class="form-label w-100" for="omni-input">
          <div class="input-toolbar">
            <span class="mb-0">Артикулы и бренды</span>
            <span class="table-help"><i class="bi bi-info-circle"></i> Формат строго PIN_BRAND, например 332101_KYB.</span>
          </div>
          <textarea
            id="omni-input"
            name="omni-input"
            class="form-control"
            rows="6"
            v-model="innerValue"
            placeholder="332101_KYB\n1600332_SACHS\nМожно вставить сразу несколько строк"
          ></textarea>
        </label>
        <div class="form-text d-flex align-items-center gap-2 mt-2">
          <i class="bi bi-magic"></i>
          <span>Используйте подчёркивание между артикулом и брендом. Разделяйте позиции новой строкой, запятой или точкой с запятой.</span>
        </div>
      </div>

      <div class="d-flex flex-wrap gap-2 btn-group-wrap">
        <button class="btn btn-gradient" :disabled="loading" @click="emitSearch">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
          <i v-else class="bi bi-search me-1"></i>
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
