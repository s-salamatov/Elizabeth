import js from '@eslint/js';
import eslintConfigPrettier from 'eslint-config-prettier';
import vue from 'eslint-plugin-vue';
import vueA11y from 'eslint-plugin-vuejs-accessibility';

export default [
  {
    ignores: ['dist', 'node_modules'],
  },
  js.configs.recommended,
  ...vue.configs['flat/recommended'],
  ...vueA11y.configs['flat/recommended'],
  {
    files: ['**/*.vue', '**/*.js', '**/*.ts'],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: 'module',
    },
    plugins: {
      'vuejs-accessibility': vueA11y,
    },
    rules: {
      'vue/multi-word-component-names': 'off',
      'vue/attributes-order': 'off',
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'vuejs-accessibility/anchor-has-content': 'error',
      'vuejs-accessibility/alt-text': 'error',
    },
  },
  {
    files: ['**/*.spec.js', '**/*.spec.ts', '**/*.test.js', '**/*.test.ts'],
    languageOptions: {
      globals: {
        describe: 'readonly',
        it: 'readonly',
        expect: 'readonly',
        beforeEach: 'readonly',
        afterEach: 'readonly',
        vi: 'readonly',
      },
    },
  },
  eslintConfigPrettier,
];
