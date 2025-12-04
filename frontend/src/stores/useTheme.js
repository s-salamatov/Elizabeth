import { ref, watch, computed } from 'vue';

const STORAGE_KEY = 'elizabeth_theme';
const theme = ref(localStorage.getItem(STORAGE_KEY) || 'system');
const systemPrefersDark = () => window.matchMedia('(prefers-color-scheme: dark)').matches;

const resolvedTheme = computed(() => {
  if (theme.value === 'system') {
    return systemPrefersDark() ? 'dark' : 'light';
  }
  return theme.value;
});

function applyTheme(value) {
  document.body.classList.remove('theme-light', 'theme-dark');
  document.body.classList.add(`theme-${value}`);
}

watch(
  resolvedTheme,
  (value) => {
    applyTheme(value);
    localStorage.setItem(STORAGE_KEY, theme.value);
  },
  { immediate: true },
);

export function useTheme() {
  return {
    theme,
    resolvedTheme,
    setTheme: (value) => {
      theme.value = value;
    },
  };
}
