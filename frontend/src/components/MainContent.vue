<template>
  <section class="main-content">
    <div class="container">
      <div class="news-grid">
        <article v-for="article in articles" :key="article.id" class="news-item">
          <img :src="article.image" :alt="article.title" />
          <div class="news-content">
            <h2>{{ article.title }}</h2>
            <p>{{ article.summary }}</p>
            <router-link :to="article.link" class="read-more">Read More</router-link>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'MainContent',
  data() {
    return {
      articles: [
        {
          id: 1,
          title: 'Global Markets Rally After Economic Data Release',
          summary: 'Stock markets worldwide saw significant gains following positive economic indicators.',
          image: 'https://via.placeholder.com/400x200',
          link: '/article/1'
        },
        {
          id: 2,
          title: 'New Tech Breakthrough in AI Development',
          summary: 'Researchers announce a major advancement in artificial intelligence algorithms.',
          image: 'https://via.placeholder.com/400x200',
          link: '/article/2'
        },
        {
          id: 3,
          title: 'Sports Event Draws Record Crowds',
          summary: 'The annual sports championship broke attendance records this year.',
          image: 'https://via.placeholder.com/400x200',
          link: '/article/3'
        }
      ]
    }
  }
}
</script>

<style lang="scss" scoped>
.main-content {
  padding: 2rem 0;

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 15px;
  }

  .news-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
  }

  .news-item {
    background: #fff;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s;

    &:hover {
      transform: translateY(-5px);
    }

    img {
      width: 100%;
      height: 200px;
      object-fit: cover;
    }

    .news-content {
      padding: 1.5rem;

      h2 {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
      }

      p {
        color: #666;
        margin-bottom: 1rem;
      }

      .read-more {
        text-decoration: none;
        color: #e74c3c;
        font-weight: 500;

        &:hover {
          text-decoration: underline;
        }
      }
    }
  }

  @media (max-width: 768px) {
    .news-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>