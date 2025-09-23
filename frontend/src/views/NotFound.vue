<template>
  <div class="not-found-page">
    <div class="not-found-container">
      <h1>404 - Page Not Found</h1>
      <p>Sorry, the page you are looking for does not exist.</p>
      <router-link to="/" class="back-link">Go to Home</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
}
</script>

<style lang="scss" scoped>
.not-found-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
}

.not-found-container {
  background: #fff;
  padding: 2rem;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 500px;
  width: 100%;

  h1 {
    font-size: 2rem;
    color: #003087;
    margin-bottom: 1rem;
  }

  p {
    font-size: 1rem;
    color: #555;
    margin-bottom: 1.5rem;
  }

  .back-link {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    background: #005b96;
    color: #fff;
    text-decoration: none;
    border-radius: 4px;
    font-size: 1rem;

    &:hover {
      background: #003087;
    }
  }
}
</style>