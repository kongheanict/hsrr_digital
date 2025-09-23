<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-100">
    <div class="w-full max-w-md bg-white shadow-md rounded-lg p-8">
      <h1 class="text-2xl font-bold text-center text-blue-700 mb-6">Login</h1>
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Username</label>
          <input
            v-model="username"
            type="text"
            required
            class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Password</label>
          <input
            v-model="password"
            type="password"
            required
            class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          />
        </div>
        <button
          type="submit"
          :disabled="loading"
          class="w-full py-2 px-4 bg-blue-600 text-white font-semibold rounded-md shadow hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {{ loading ? "Logging in..." : "Login" }}
        </button>
        <p v-if="error" class="text-sm text-red-600 text-center">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useAuthStore, api } from "../stores/auth";

const authStore = useAuthStore();
const username = ref("");
const password = ref("");
const loading = ref(false);
const error = ref(null);

const handleLogin = async () => {
  loading.value = true;
  error.value = null;

  try {
    const response = await api.post("/token/", {
      username: username.value,
      password: password.value,
    });

    if (response.data.access && response.data.refresh) {
      authStore.login({
        user: { username: username.value },
        access: response.data.access,
        refresh: response.data.refresh,
      });
      // this.$router.push('/');
      window.location.href = "/"; // redirect
    } else {
      error.value = "Login failed. Please try again.";
    }
  } catch (err) {
    if (err.response?.status === 401) {
      error.value = "Invalid username or password";
    } else {
      error.value = "Something went wrong. Please try again later.";
    }
  } finally {
    loading.value = false;
  }
};
</script>
