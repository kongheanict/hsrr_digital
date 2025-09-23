<template>
  <nav class="bg-white shadow sticky top-0 z-50">
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
          HSRR DIGITAL
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
            to="/quizzes"
            class="text-gray-700 hover:text-blue-600"
            active-class="text-blue-600 underline"
          >
            តេស្ត
          </router-link>
        </div>
      </div>

      <!-- Right: User Menu -->
      <div class="flex items-center gap-4">
        <template v-if="authStore.isAuthenticated">
          <div class="hidden md:block text-gray-700">
            <span class="mr-2">Welcome, {{ authStore.user.username }}</span>
            <router-link
              to="/profile"
              class="hover:text-blue-600"
            >
              Profile
            </router-link>
          </div>
          <button
            @click="logout"
            class="hover:text-blue-600 text-gray-700"
          >
            <i class="fa-solid fa-arrow-right-from-bracket"></i>
          </button>
        </template>

        <router-link
          v-else
          to="/login"
          class="hover:text-blue-600 text-gray-700"
        >
          Login
        </router-link>
      </div>
    </div>

    <!-- Mobile dropdown overlay menu -->
    <transition name="slide-down">
      <div
        v-show="isSidebarOpen"
        class="md:hidden absolute top-full left-0 w-full bg-white shadow-lg border-t border-gray-200 z-40 px-4 py-3 space-y-3"
      >
        <router-link
          to="/"
          class="block text-gray-700 hover:text-blue-600 font-semibold"
          active-class="text-blue-600 underline"
          @click="toggleSidebar"
        >
          ទំព័រដើម
        </router-link>
        <router-link
          to="/courses"
          class="block text-gray-700 hover:text-blue-600 font-semibold"
          active-class="text-blue-600 underline"
          @click="toggleSidebar"
        >
          វគ្គសិក្សា
        </router-link>
        <router-link
          to="/quizzes"
          class="block text-gray-700 hover:text-blue-600 font-semibold"
          active-class="text-blue-600 underline"
          @click="toggleSidebar"
        >
          តេស្ត
        </router-link>

        <div v-if="authStore.isAuthenticated" class="border-t border-gray-200 pt-3">
          <router-link
            to="/profile"
            class="block text-gray-700 hover:text-blue-600 font-semibold"
            @click="toggleSidebar"
          >
            Profile
          </router-link>
          <button
            @click="logout"
            class="block w-full text-left text-gray-700 hover:text-blue-600 mt-2 font-semibold"
          >
            Logout
          </button>
        </div>
        <router-link
          v-else
          to="/login"
          class="block text-gray-700 hover:text-blue-600 font-semibold"
          @click="toggleSidebar"
        >
          Login
        </router-link>
      </div>
    </transition>
  </nav>
</template>

<script>
import { useAuthStore } from '../stores/auth'

export default {
  name: 'Navbar',
  props: {
    isSidebarOpen: { type: Boolean, default: false }
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
  }
}
</script>

<style scoped>
/* Slide down transition */
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
