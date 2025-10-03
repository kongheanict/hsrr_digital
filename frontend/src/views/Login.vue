<template>
  <div class="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-100 to-white">
    <div class="w-full max-w-md md:bg-white md:shadow-lg rounded-xl p-6 md:p-8">
      <!-- Logo Placeholder -->
      <div class="flex justify-center mb-6">
        <img src="../assets/images/logo1.png" alt="LMS Logo" class="h-20" />
      </div>
      <h1 class="text-2xl font-bold text-center text-gray-900 mb-10">វិទ្យុាល័យហ៊ុនសែនរុងរឿង</h1>
      <!-- <p class="text-center text-sm text-gray-600 mb-6">សូមបញ្ចូលអត្តលេខ និងលេខសម្ងាត់ដើម្បីចូលប្រើប្រាស់</p> -->
      <form @submit.prevent="handleLogin" class="space-y-5">
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700">លេខសម្គាល់</label>
          <input
            id="username"
            v-model="username"
            type="text"
            required
            placeholder="Enter your username or email"
            class="mt-1 block w-full rounded-md border bg-white border-gray-300 px-4 py-2 text-sm focus:border-blue-500 focus:ring-blue-500 transition duration-150 ease-in-out"
          />
        </div>
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700">លេខសម្ងាត់</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            placeholder="Enter your password"
            class="mt-1 block w-full rounded-md border bg-white border-gray-300 px-4 py-2 text-sm focus:border-blue-500 focus:ring-blue-500 transition duration-150 ease-in-out"
          />
        </div>
        <div class="flex items-center justify-between text-sm">
          <a href="/forgot-password" class="text-blue-600 hover:text-blue-800 font-medium">ភ្លេចលេខសម្ងាត់?</a>
        </div>
        <button
          type="submit"
          :disabled="loading"
          class="w-full py-3 px-4 bg-blue-600 text-white font-semibold rounded-md shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition duration-150 ease-in-out"
        >
          {{ loading ? "កំពុងចូល..." : "ចូល" }}
        </button>
        <p v-if="error" class="text-sm text-red-600 text-center mt-2">{{ error }}</p>
        <p class="text-center text-sm text-gray-600 mt-4">
          មិនទាន់មានគណនី? <a href="/register" class="text-blue-600 hover:text-blue-800 font-medium">ស្នើសុំគណនី</a>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useAuthStore, api } from "../stores/auth";

const authStore = useAuthStore();
const username = ref("6240004886");
const password = ref("123@Gov.kh");
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
      window.location.href = "/"; // Redirect to dashboard instead of root
    } else {
      error.value = "Login failed. Please check your credentials.";
    }
  } catch (err) {
    if (err.response?.status === 401) {
      error.value = "Invalid username or password";
    } else {
      error.value = "An error occurred. Please try again later.";
    }
  } finally {
    loading.value = false;
  }
};
</script>