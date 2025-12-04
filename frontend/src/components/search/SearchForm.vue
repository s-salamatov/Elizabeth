<template>
  <div class="card mb-3">
    <div class="card-body">
      <div class="mb-3">
        <label class="form-label w-100" for="omni-input">
          <div class="input-toolbar">
            <span class="table-help">
              <button class="btn btn-ghost btn-link btn-sm" @click="reset" type="button">
                <i class="bi bi-eraser me-1"></i> Очистить поле ввода
              </button>
            </span>
          </div>
          <textarea
            id="omni-input"
            name="omni-input"
            class="form-control"
            rows="6"
            v-model="innerValue"
            placeholder="Введите артикул и бренд или их список для поиска"
          ></textarea>
        </label>
        <div class="form-text d-flex align-items-center gap-2 mt-2">
          <i class="bi bi-magic"></i>
          <span>Формат: АРТИКУЛ_БРЕНД. Для поиска сразу нескольких позиций введите каждую с новой строки или разделите их знаками <b>, ;</b></span>
        </div>
      </div>

      <div class="d-flex flex-wrap gap-2 btn-group-wrap">
        <button class="btn btn-outline-gradient" :disabled="loading" @click="emitSearch(true)">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
          <i v-else class="bi bi-search me-1"></i>
          Найти
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

const emitSearch = (preserve = true) => {
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
