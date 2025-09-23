import { createApp } from 'vue'
import App from './App.vue'
import { createI18n } from 'vue-i18n';
import router from './router'
import { createPinia } from 'pinia'
import './assets/styles/main.css'
import '@fortawesome/fontawesome-free/css/all.min.css'
import axios from 'axios'
import { useAuthStore } from './stores/auth'



// Khmer translations
const messages = {
  km: {
    courses: 'វគ្គសិក្សា',
    lessons: 'មេរៀន',
    parts: 'ផ្នែក',
    title: 'ចំណងជើង',
    description: 'ការពិពណ៌នា',
    loading: 'កំពុងផ្ទុក...',
    error: 'កំហុស',
  },
};

const i18n = createI18n({
  legacy: false,
  locale: 'km',
  messages,
});

// Set up Axios interceptor for token refresh
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response.status === 401) {
      const authStore = useAuthStore()
      try {
        await authStore.refreshAccessToken()
        error.config.headers['Authorization'] = `Bearer ${authStore.accessToken}`
        return axios(error.config)
      } catch (refreshError) {
        authStore.logout()
        router.push('/login')
      }
    }
    return Promise.reject(error)
  }
)
const app = createApp(App)
app.use(router)
app.use(i18n);
app.use(createPinia())
app.mount('#app')