<template>
  <!-- Mobile Top Bar -->
  <nav class="shadow shadow-blue-200 bg-gray-100 fixed top-0 w-full z-50 md:hidden">
    <div class="flex items-center px-4 py-3">
      <!-- Back Icon -->
      <button @click="$router.go(-1)" class="text-gray-600 hover:text-blue-600 mr-4">
        <i class="fas fa-arrow-left text-sm"></i>
      </button>
      <!-- Title -->
      <h1 class="text-sm font-semibold text-gray-600">{{ title }}</h1>
    </div>
  </nav>

  <!-- Mobile Bottom Bar -->
  <nav class="bg-blue-100 shadow fixed bottom-0 w-full z-50 md:hidden">
    <div class="flex justify-around items-center px-4 py-3">
      <!-- Home -->
      <router-link to="/" class="flex flex-col items-center text-gray-700 hover:text-blue-600">
        <i class="fas fa-home text-lg"></i>
        <span class="text-xs pt-2 font-semibold">ទំព័រដើម</span>
      </router-link>
      <!-- horizontal divider -->
      <div class="border-l h-10 border-gray-300"></div>
      <!-- Learn -->
      <router-link to="/courses" class="flex flex-col items-center text-gray-700 hover:text-blue-600">
        <i class="fas fa-book text-lg"></i>
        <span class="text-xs pt-2 font-semibold">វគ្គសិក្សា</span>
      </router-link>

      <div class="border-l h-10 border-gray-300"></div>
      <!-- Measure -->
      <router-link v-if="['student', 'admin'].includes(userRole)" to="/quizzes" class="flex flex-col items-center text-gray-700 hover:text-blue-600">
        <i class="fas fa-ruler text-lg"></i>
        <span class="text-xs pt-2 font-semibold">តេស្ត</span>
      </router-link>

      <div v-if="['student', 'admin'].includes(userRole)" class="border-l h-10 border-gray-300"></div>

      <router-link v-if="['teacher', 'admin'].includes(userRole)" to="/ask-leave-form" class="flex flex-col items-center text-gray-700 hover:text-blue-600">
        <i class="fas fa-ruler text-lg"></i>
        <span class="text-xs pt-2 font-semibold">សុំច្បាប់</span>
      </router-link>

      <div v-if="['teacher', 'admin'].includes(userRole)" class="border-l h-10 border-gray-300"></div>

      <!-- Profile/Login -->
      <router-link to="/profile" v-if="authStore.isAuthenticated" class="flex flex-col items-center text-gray-700 hover:text-blue-600">
        <i class="fas fa-user text-lg"></i>
        <span class="text-xs pt-2 font-semibold">គណនី</span>
      </router-link>

      <router-link to="/login" v-else class="flex flex-col items-center text-gray-700 hover:text-blue-600">
        <i class="fas fa-sign-in-alt text-lg"></i>
        <span class="text-xs pt-2 font-semibold">Login</span>
      </router-link>
      
      <div class="border-l h-10 border-gray-300"></div>
      <!-- Record -->
      <a @click="logout" class="flex flex-col items-center text-gray-700 hover:text-blue-600">
        <i class="fa-solid fa-arrow-right-from-bracket"></i>
        <span class="text-xs pt-2 font-semibold">ចាកចេញ</span>
      </a>
    </div>
  </nav>

  <!-- Desktop nav (unchanged) -->
  <nav class="bg-white shadow sticky top-0 z-50 hidden md:block">
    <div class="max-w-7xl mx-auto flex justify-between items-center px-4 py-3 relative">
      <!-- Left: Logo + Nav -->
      <div class="flex items-center">
        <!-- Hamburger (mobile only) -->
        <button
          class="md:hidden flex flex-col justify-between w-6 h-5 focus:outline-none z-50"
          @click="toggleSidebar"
        >
          <span
            class="h-0.5 w-6 bg-gray-800 transition-transform duration-300"
            :class="{ 'rotate-45 translate-y-2': isSidebarOpen }"
          ></span>
          <span
            class="h-0.5 w-6 bg-gray-800 transition-opacity duration-300"
            :class="{ 'opacity-0': isSidebarOpen }"
          ></span>
          <span
            class="h-0.5 w-6 bg-gray-800 transition-transform duration-300"
            :class="{ '-rotate-45 -translate-y-2': isSidebarOpen }"
          ></span>
        </button>

        <!-- Logo -->
        <router-link
          to="/"
          class="ml-3 text-xl font-bold text-gray-800 hover:text-blue-600"
        >
          <img src="../assets/images/logo-text-black.png" class="" alt="{{ title }}" style="height: 30px;" />
        </router-link>

        <!-- Desktop nav -->
        <div class="hidden md:flex ml-6 space-x-6 text-sm font-semibold">
          <router-link
            to="/"
            class="text-gray-700 hover:text-blue-600"
            active-class="text-blue-600 underline"
          >
            ទំព័រដើម
          </router-link>
          <router-link
            to="/courses"
            class="text-gray-700 hover:text-blue-600"
            active-class="text-blue-600 underline"
          >
            វគ្គសិក្សា
          </router-link>
          <router-link
            v-if="['student', 'admin'].includes(userRole)"
            to="/quizzes"
            class="text-gray-700 hover:text-blue-600"
            active-class="text-blue-600 underline"
          >
            តេស្ត
          </router-link>
          <router-link
            v-if="['teacher', 'admin'].includes(userRole)"
            to="/ask-leave-form"
            class="text-gray-700 hover:text-blue-600"
            active-class="text-blue-600 underline"
          >
            សុំច្បាប់
          </router-link>
        </div>
      </div>

      <!-- Right: User Menu -->
      <div class="flex items-center gap-4">
        <template v-if="authStore.isAuthenticated">
          <div class="hidden md:block text-gray-700">
            <span class="mr-2 text-sm">ស្វាគមន៍, <b>{{ userFullName }}</b></span>
          </div>
          <button
            @click="logout"
            class="hover:text-blue-600 text-gray-700 cursor-pointer"
          >
            <i class="fa-solid fa-arrow-right-from-bracket"></i>
          </button>
        </template>

        <router-link
          v-else
          to="/login"
          class="hover:text-blue-600 text-gray-700 cursor-pointer"
        >
          Login
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script>
import { useAuthStore } from '../stores/auth';

export default {
  name: 'Navbar',
  props: {
    isSidebarOpen: { type: Boolean, default: false },
    title: { type: String, default: 'LMS' }
  },
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  methods: {
    toggleSidebar() {
      this.$emit('toggle-sidebar', !this.isSidebarOpen)
    },
    logout() {
      this.authStore.logout()
      this.$router.push('/login')
    }
  },
  computed: {
    userRole() {
      return this.authStore.user ? this.authStore.getRole : null;
    },
    userFullName() {
      return this.authStore.user ? this.authStore.getFullName : ''; 
    }
  }
}
</script>

<style scoped>
/* Slide down transition (kept for potential future use) */
.slide-down-enter-from {
  transform: translateY(-10px);
  opacity: 0;
}
.slide-down-enter-to {
  transform: translateY(0);
  opacity: 1;
}
.slide-down-enter-active {
  transition: all 0.3s ease-out;
}
.slide-down-leave-from {
  transform: translateY(0);
  opacity: 1;
}
.slide-down-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
.slide-down-leave-active {
  transition: all 0.3s ease-in;
}
</style>