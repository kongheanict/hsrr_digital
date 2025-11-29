import './assets/css/main.css'

import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'

import App from './App.vue'
import { useAuthStore } from './stores/auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

const router = createRouter({
  routes: [
    { path: '/login', component: () => import('./pages/login.vue'), meta: { layout: 'auth' } },
    { path: '/', component: () => import('./pages/index.vue'), meta: { layout: 'default' } },
    { path: '/inbox', component: () => import('./pages/inbox.vue'), meta: { layout: 'default' } },
    { path: '/customers', component: () => import('./pages/customers.vue'), meta: { layout: 'default' } },
    {
      path: '/settings',
      component: () => import('./pages/settings.vue'),
      meta: { layout: 'default' },
      children: [
        { path: '', component: () => import('./pages/settings/index.vue') },
        { path: 'members', component: () => import('./pages/settings/members.vue') },
        { path: 'notifications', component: () => import('./pages/settings/notifications.vue') },
        { path: 'security', component: () => import('./pages/settings/security.vue') },
      ]
    }
  ],
  history: createWebHistory()
})

// Initialize auth from localStorage
const authStore = useAuthStore()
authStore.initAuth()

// Navigation guard to protect routes
router.beforeEach((to, _from, next) => {
  const isAuthPage = to.meta.layout === 'auth'
  const isAuthenticated = authStore.isAuthenticated

  if (!isAuthPage && !isAuthenticated) {
    // Redirect to login if trying to access protected page without auth
    next('/login')
  } else if (isAuthPage && isAuthenticated) {
    // Redirect to home if trying to access login while already authenticated
    next('/')
  } else {
    next()
  }
})

app.use(router)

app.mount('#app')
