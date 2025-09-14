<template>
    <div>
        <router-link to="/">Home</router-link>
        <router-link to="/about">About</router-link>
        <router-link to="/login">Login</router-link>
    </div>
</template>

<script setup>
    import { RouterLink } from 'vue-router';
</script>