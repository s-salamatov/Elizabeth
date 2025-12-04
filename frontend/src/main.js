import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './assets/styles.scss';
import 'bootstrap';
import { useTheme } from './stores/useTheme';

const app = createApp(App);
app.use(router);

// Initialize theme early so login/unauth pages get the stored or system preference
useTheme();

app.mount('#app');
