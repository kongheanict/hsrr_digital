<template>
  <div class="min-h-screen bg-gray-50 px-4 sm:px-6 lg:px-8 py-18 md:py-8 max-w-7xl mx-auto">
    <!-- Hero Section -->
    <div class="bg-gradient-to-r from-indigo-600 to-blue-500 text-white rounded-sm shadow-lg p-6 mb-8">
      <h1 class="text-2xl sm:text-3xl font-bold">{{ $t('កម្រងសំណួរប្រឡង') }}</h1>
      <p class="mt-2 text-sm sm:text-base opacity-90">{{ $t('សាកល្បងចំណេះដឹងរបស់អ្នកជាមួយកម្រងសំណួរដែលបានរៀបចំឡើង។') }}</p>
    </div>

    <!-- Filter and Search Section -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 gap-4">
      <div class="relative w-full sm:w-48">
        <select
          v-model="selectedFilter"
          class="w-full bg-white px-4 py-2 pr-8 border border-gray-200 rounded-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 appearance-none transition-all duration-200"
        >
          <option value="all">{{ $t('All Quizzes') }}</option>
          <option value="beginner">{{ $t('Beginner') }}</option>
          <option value="intermediate">{{ $t('Intermediate') }}</option>
          <option value="advanced">{{ $t('Advanced') }}</option>
        </select>
        <svg class="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center h-48 bg-white rounded-sm shadow-md p-6">
      <div class="animate-spin rounded-smll h-12 w-12 border-t-4 border-indigo-600"></div>
      <p class="ml-4 text-lg font-medium text-gray-700">{{ $t('កំពុងផ្ទុកទិន្នន័យកម្រងសំណួរ...') }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center px-6 py-6 bg-red-50 rounded-sm shadow-md">
      <p class="text-lg font-medium text-red-600">{{ error }}</p>
      <button @click="fetchQuizzes" class="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-sm hover:bg-indigo-700 transition duration-200">
        {{ $t('ព្យាយាមម្តងទៀត') }}
      </button>
    </div>

    <!-- Quizzes Content -->
    <div v-else>
      <div v-if="filteredQuizzes.length === 0" class="text-center text-gray-600 font-medium py-8 bg-white rounded-sm shadow-md px-6">
        {{ $t('គ្មានកម្រងសំណួរណាមួយឡើយ។') }}
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-6">
        <div
          v-for="quiz in filteredQuizzes"
          :key="quiz.id"
          class="bg-white rounded-sm p-5 shadow-md hover:shadow-lg transition-all duration-300 border border-gray-100 flex flex-col"
        >
          <div class="flex items-center mb-4">
            <img src="../assets/images/quiz.png" class="h-10 mr-2" alt="">
            <h2 class="text-lg font-semibold text-gray-900 line-clamp-2">{{ quiz.title }}</h2>
          </div>
          <div class="space-y-2 text-sm text-gray-500 mb-4 flex-grow">
            <p>{{ $t('កាលបរិច្ឆេទ') }}: {{ formatDate(quiz.start_time) }}</p>
            <p>{{ $t('រយៈពេល') }}: {{ quiz.time_limit }}</p>
          </div>
          <div class="mt-auto">
            <router-link
              v-if="!quiz.has_attempted"
              :to="{ name: 'QuizPage', query: { quizId: quiz.id } }"
              class="inline-block bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-sm transition duration-200 w-full text-center"
            >
              {{ $t('ចាប់ផ្តើមកម្រងសំណួរ') }}
            </router-link>
            <router-link
              v-else
              :to="{ name: 'QuizReviewPage', query: { quizId: quiz.id } }"
              class="inline-block bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-sm transition duration-200 w-full text-center"
            >
              {{ $t('ពិនិត្យចម្លើយ') }}
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useQuizStore } from '../stores/quiz';

const { t } = useI18n();
const quizStore = useQuizStore();
const quizzes = ref([]);
const loading = ref(false);
const error = ref(null);
const selectedFilter = ref('all');

const fetchQuizzes = async () => {
  loading.value = true;
  await quizStore.fetchQuizzes();
  quizzes.value = quizStore.quizzes;
  loading.value = false;
  if (quizStore.error) {
    error.value = quizStore.error;
  }
};

const filteredQuizzes = computed(() => {
  if (selectedFilter.value === 'all') return quizzes.value;
  return quizzes.value.filter((quiz) =>
    quiz.level?.toLowerCase() === selectedFilter.value.toLowerCase()
  );
});

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('km-KH', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

onMounted(() => {
  fetchQuizzes();
});
</script>

<style lang="css" scoped>
/* Empty style block to satisfy Vue's scoped requirement */
</style>