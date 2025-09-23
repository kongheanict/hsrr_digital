<template>
  <div v-if="show" class="loading-overlay">
    <div class="spinner"></div>
    <p class="loading-text">{{ text || 'Loading...' }}</p>
  </div>
</template>

<script lang="ts" setup>
import { defineProps } from 'vue';

const props = defineProps<{
  show: boolean;
  text?: string;
}>();
</script>

<style scoped lang="scss">
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255,255,255,0.85);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 9999;

  .spinner {
    width: 60px;
    height: 60px;
    border: 6px solid #cbd5e1;
    border-top-color: #2563eb;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
  }

  .loading-text {
    font-size: 1.1rem;
    font-weight: 600;
    color: #2563eb;
    text-align: center;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
}
</style>
