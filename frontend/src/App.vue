<template>
  <div id="app" class="bg-gradient-to-br from-gray-50 to-gray-50">
    <Navbar :title="title" v-if="authStore.isAuthenticated" @toggle-sidebar="toggleSidebar" :is-sidebar-open="isSidebarOpen" />
    <div class="" v-if="authStore.isAuthenticated">
      <router-view/>
    </div>
    <router-view v-else />
  </div>
</template>

<script>
import Navbar from './components/Navbar.vue'
import { useAuthStore } from './stores/auth'
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'App',
  components: {
    Navbar
  },
  setup() {
    const authStore = useAuthStore()
    const route = useRoute()

    // Compute the title based on the current route
    const title = computed(() => {
      switch (route.name) {
        case 'HomePage':
          return 'ទំព័រដើម'
        case 'CoursePage':
          return 'វគ្គសិក្សា'
        case 'Quizzes':
          return 'កម្រងតេស្ត'
        case 'QuizReviewPage':
          return 'កម្រងសំណួរ'
        case 'AskLeave':
          return 'ទម្រង់សុំច្បាប់'
        case 'QuizPage':
          return 'បំពេញតេស្ត'
        default:
          return 'Learn'
      }
    })

    return { authStore, title }
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
  },
  // Watch for route changes to update the title
  watch: {
    '$route' (to) {
      this.title = this.getTitleFromRoute(to.name)
    }
  },
  methods: {
    getTitleFromRoute(routeName) {
      switch (routeName) {
        case 'HomePage':
          return 'ទំព័រដើម'
        case 'CoursePage':
          return 'វគ្គសិក្សា'
        case 'Quizzes':
          return 'កម្រងតេស្ត'
        case 'profile':
          return 'Profile'
        default:
          return 'Learn'
      }
    }
  }
}
</script>

<style lang="scss">
@use './assets/styles/main.css' as*;
</style>