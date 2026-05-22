import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import { router } from './router';
import './styles/main.css';
import { useUiStore } from './stores/ui';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
useUiStore(pinia).hydrateDemoMode();
app.use(router).mount('#app');
