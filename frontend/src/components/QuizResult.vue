<!-- src/components/QuizResult.vue -->
<template>
  <div class="result-container">
    <h2>Quiz Results</h2>
    <p v-if="attempt">Your score: {{ attempt.score }}%</p>
    <p v-else>Loading results...</p>
    <router-link :to="{ name: 'Quizzes' }">Back to Quizzes</router-link>
  </div>
</template>

<script>
import { useQuizStore } from '../stores/quiz';

export default {
  data() {
    return {
      attempt: null
    };
  },
  async created() {
    await useQuizStore().fetchAttempts();
    this.attempt = useQuizStore().attempts.find(a => a.quiz.id == this.$route.params.quizId);
  }
};
</script>

<style lang="scss">
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Khmer&display=swap');

.result-container {
  padding: 20px;
  font-family: 'Noto Sans Khmer', sans-serif;
  max-width: 800px;
  margin: 0 auto;

  h2 {
    color: #101110;
  }

  a {
    color: #101110;
    text-decoration: none;
    margin-top: 20px;
    display: inline-block;
  }

  @media (max-width: 600px) {
    padding: 10px;
  }
}
</style>