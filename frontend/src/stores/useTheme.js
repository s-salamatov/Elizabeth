import { ref, watch, computed } from 'vue';

const STORAGE_KEY = 'elizabeth_theme';
const theme = ref(localStorage.getItem(STORAGE_KEY) || 'system');
const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
const systemPreference = ref(mediaQuery.matches);

const handleSystemChange = (event) => {
  systemPreference.value = event.matches;
};

if (mediaQuery.addEventListener) {
  mediaQuery.addEventListener('change', handleSystemChange);
} else if (mediaQuery.addListener) {
  mediaQuery.addListener(handleSystemChange);
}

const resolvedTheme = computed(() => {
  if (theme.value === 'system') {
    return systemPreference.value ? 'dark' : 'light';
  }
  return theme.value;
});

function applyTheme(value) {
  document.body.classList.remove('theme-light', 'theme-dark');
  document.body.classList.add(`theme-${value}`);
  document.documentElement.classList.add('theme-transition');
  window.clearTimeout(applyTheme._timer);
  applyTheme._timer = window.setTimeout(() => {
    document.documentElement.classList.remove('theme-transition');
  }, 320);
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
