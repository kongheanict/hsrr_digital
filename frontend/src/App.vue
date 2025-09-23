<template>
  <div id="app" class="bg-grey-100">
    <Navbar @toggle-sidebar="toggleSidebar" :is-sidebar-open="isSidebarOpen" />
    <div class="app-container" v-if="authStore.isAuthenticated">
      <router-view class="main-content" />
    </div>
    <router-view v-else />
  </div>
</template>

<script>
import Navbar from './components/Navbar.vue'
import Sidebar from './components/Sidebar.vue'
import { useAuthStore } from './stores/auth'

export default {
  name: 'App',
  components: {
    Navbar,
    Sidebar
  },
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      isSidebarOpen: false
    }
  },
  methods: {
    toggleSidebar(isOpen) {
      this.isSidebarOpen = isOpen
    }
  }
}
</script>

<style lang="scss">
@use './assets/styles/main.css' as*;
</style>