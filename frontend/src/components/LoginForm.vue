<template>
  <form @submit.prevent="submitLogin" class="login-form">
    <input v-model="username" type="text" placeholder="Username" required />
    <input v-model="password" type="password" placeholder="Password" required />
    <button type="submit">Login</button>
  </form>
</template>

<script setup>
import { ref } from "vue";
import { useAuthStore } from "../stores/auth";

const username = ref("");
const password = ref("");
const authStore = useAuthStore();

const submitLogin = async () => {
  try {
    await authStore.login(username.value, password.value);
    alert("Login success");
  } catch (err) {
    alert("Login failed");
  }
};
</script>

<style scoped lang="scss">
.login-form {
  display: flex;
  flex-direction: column;
  max-width: 300px;
  margin: 2rem auto;
  input {
    margin-bottom: 1rem;
    padding: 0.5rem;
  }
  button {
    padding: 0.5rem;
  }
}
</style>
