<template>
  <div class="container mx-auto p-4">
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-t-4 border-blue-500"></div>
      <p class="ml-4 text-lg text-gray-600">{{ $t('Loading quiz data...') }}</p>
    </div>
    <div v-else-if="error" class="text-center text-xl text-red-500">{{ error }}</div>
    <div v-else>
      <h1 class="text-2xl font-bold mb-6">Available Quizzes</h1>
      <div v-if="quizzes.length === 0" class="text-gray-600">No quizzes are currently available.</div>
      
      <div v-else class="bg-blue-400">
        <div v-for="quiz in quizzes" :key="quiz.id" class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-semibold">{{ quiz.title }}</h2>
          <p class="text-gray-600 mb-4">{{ quiz.description }}</p>
          <p class="text-sm text-gray-500">កាលបរិច្ឆេទ: {{ quiz.start_time }}</p>
          <p class="text-sm text-gray-500">រយៈពេល: {{ quiz.time_limit }}</p>
          
          <div class="mt-4">
            <router-link 
              v-if="!quiz.has_attempted"
              :to="{ name: 'QuizPage', query: { quizId: quiz.id } }"
              class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
              Start Quiz
            </router-link>

            <router-link 
              v-else
              :to="{ name: 'QuizReviewPage', query: { quizId: quiz.id } }"
              class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
            >
              Review Answers
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useQuizStore } from '../stores/quiz';

const quizStore = useQuizStore();
const quizzes = ref([]);
const loading = ref(false);
const error = ref(null);

onMounted(async () => {
  loading.value = true;
  await quizStore.fetchQuizzes();
  quizzes.value = quizStore.quizzes;
  loading.value = false;
  if (quizStore.error) {
    error.value = quizStore.error;
  }
});
</script>
