<template>
  <aside class="sidebar" :class="{ 'sidebar--open': isSidebarOpen }">
   
  </aside>
</template>

<script>
import { useI18n } from 'vue-i18n';
export default {
  name: 'Sidebar',
  props: {
    isSidebarOpen: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style lang="scss" scoped>
.sidebar {
  width: 200px;
  background: #f0f0f0;
  padding: 20px;
  border-radius: 4px;
  margin-right: 20px;
  display: none;
  transition: transform 0.3s ease;

  ul {
    list-style: none;
    padding: 0;
  }

  li {
    margin-bottom: 10px;
  }

  a {
    text-decoration: none;
    color: #005b96;
    font-weight: 500;

    &.router-link-active,
    &:hover {
      color: #003087;
      text-decoration: underline;
    }
  }

  @media (max-width: 768px) {
    position: fixed;
    top: 65px;
    left: 0;
    height: 100%;
    display: block;
    transform: translateX(-100%);
    z-index: 1000;


    &.sidebar--open {
      transform: translateX(0);
      box-shadow: 2px 0 5px rgba(0, 0, 0, 0.2);
    }
  }
}
</style>