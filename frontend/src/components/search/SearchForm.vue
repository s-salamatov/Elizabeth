<template>
  <div class="card search-card" :class="{ collapsed }">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-start flex-wrap gap-2 mb-3">
        <div>
          <h5 class="card-title mb-1">Поиск товаров</h5>
          <p class="text-muted mb-0" v-if="!collapsed">Введите артикул и бренд или несколько позиций списком.</p>
        </div>
        <div class="d-flex gap-2 align-items-center">
          <button
            v-if="canCollapse"
            class="btn btn-ghost btn-sm"
            type="button"
            @click="$emit('toggle-collapse')"
          >
            <i class="bi" :class="collapsed ? 'bi-chevron-down' : 'bi-chevron-up'"></i>
            {{ collapsed ? 'Развернуть' : 'Свернуть' }}
          </button>
          <button class="btn btn-ghost btn-sm" @click="reset" type="button">
            <i class="bi bi-eraser me-1"></i>
            Очистить
          </button>
        </div>
      </div>

      <template v-if="!collapsed">
        <transition name="fade-collapse">
          <div v-show="!collapsed">
            <label class="form-label w-100" for="omni-input">
              <textarea
                id="omni-input"
                name="omni-input"
                class="form-control search-textarea"
                rows="1"
                ref="textareaRef"
                v-model="innerValue"
                @input="autoResize"
                placeholder="Введите артикул и бренд или их список для поиска"
              ></textarea>
            </label>
            <div class="form-text d-flex align-items-center gap-2 mt-2 helper-text">
              <i class="bi bi-magic"></i>
              <span>Формат: АРТИКУЛ_БРЕНД. Для поиска нескольких позиций вводите с новой строки или разделяйте знаками <b>, ;</b></span>
            </div>
          </div>
        </transition>
      </template>

      <div
        v-else
        class="collapsed-preview"
        role="button"
        tabindex="0"
        @click="$emit('toggle-collapse')"
        @keydown.enter.prevent="$emit('toggle-collapse')"
        @keydown.space.prevent="$emit('toggle-collapse')"
      >
        <i class="bi bi-text-left"></i>
        <span class="text-truncate">{{ previewText }}</span>
        <i class="bi bi-chevron-down ms-auto"></i>
      </div>

      <div class="d-flex flex-wrap gap-2 align-items-center mt-3">
          <button class="btn btn-gradient" :disabled="loading" @click="emitSearch(true)">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
            <i v-else class="bi bi-search me-1"></i>
            Найти
          </button>
        <span class="text-muted small" v-if="loading">Выполняем поиск…</span>
      </div>
      <AlertMessage v-if="error" :message="error" variant="danger" class="mt-3" />
    </div>
  </div>
</template>

<script setup>
import { nextTick, computed, onMounted, ref, watch } from 'vue';
import AlertMessage from '../common/AlertMessage.vue';

const props = defineProps({
  modelValue: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  collapsed: { type: Boolean, default: false },
  canCollapse: { type: Boolean, default: false },
});

const emit = defineEmits(['update:modelValue', 'submit', 'toggle-collapse']);
const innerValue = ref(props.modelValue);
const textareaRef = ref(null);

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

const previewText = computed(() => innerValue.value.trim() || 'Запрос пока пуст');

const autoResize = () => {
  const el = textareaRef.value;
  if (!el) return;
  el.style.height = 'auto';
  el.style.height = `${Math.min(el.scrollHeight, 480)}px`;
};

onMounted(() => {
  nextTick(autoResize);
});

watch(innerValue, () => nextTick(autoResize));
</script>
