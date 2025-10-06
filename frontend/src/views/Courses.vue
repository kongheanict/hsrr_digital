<template>
  <div class="min-h-screen bg-gray-50 px-4 sm:px-6 lg:px-8 py-18 md:py-8 max-w-7xl mx-auto">
    <!-- Hero Section -->
    <div class="bg-gradient-to-r from-indigo-600 to-blue-500 text-white rounded-sm shadow-lg p-6 mb-4">
      <h1 class="text-2xl sm:text-3xl font-bold">{{ $t('courses') }}</h1>
      <p class="mt-2 text-sm sm:text-base opacity-90">Explore a wide range of courses to enhance your skills and knowledge.</p>
    </div>

    <!-- Filter and Search Section -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 gap-4">
      <!-- Filter Dropdown -->
      <div class="relative w-full sm:w-48">
        <select
          v-model="selectedFilter"
          class="w-full bg-white px-4 py-2 pr-8 border border-gray-200 rounded-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 appearance-none transition-all duration-200"
        >
          <option value="all">{{ $t('All Courses') }}</option>
          <option value="beginner">{{ $t('Beginner') }}</option>
          <option value="intermediate">{{ $t('Intermediate') }}</option>
          <option value="advanced">{{ $t('Advanced') }}</option>
        </select>
        <svg class="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
      <!-- Search Input -->
      <div class="relative w-full sm:w-96">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="$t('ស្វែងរកចំណងជើង...')"
          class="w-full bg-white px-4 py-2 pl-10 border border-gray-200 rounded-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200"
        />
        <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
    </div>

    <!-- Loading States -->
    <div v-if="store.loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-t-4 border-indigo-600"></div>
      <p class="ml-4 text-lg text-gray-600 font-medium">{{ $t('Loading quiz data...') }}</p>
    </div>
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-t-4 border-indigo-600"></div>
      <p class="ml-4 text-lg text-gray-600 font-medium">{{ $t('Loading quiz data...') }}</p>
    </div>
    <div v-else-if="searchLoading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-t-4 border-indigo-600"></div>
      <p class="ml-4 text-lg text-gray-600 font-medium">{{ $t('Loading quiz data...') }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="store.error" class="text-center px-5 py-5 bg-red-50 text-red-600 rounded-sm shadow-sm">
      {{ $t('error') }}: {{ store.error }}
    </div>

    <!-- Courses Grid -->
    <div class="grid grid-cols-1 gap-6">
      <CourseCard
        v-for="course in filteredCourses"
        :key="course.id"
        :course="course"
        @complete="store.completeCourse(course.id)"
        class="bg-white rounded-sm shadow-md hover:shadow-lg transition-shadow duration-300"
      />
      <p v-if="filteredCourses.length === 0" class="text-center col-span-full text-gray-500 text-lg font-medium py-12">
        {{ $t('មិនមានវគ្គសិក្សា') }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useCourseStore } from '../stores/course';
import CourseCard from '../components/CourseCard.vue';
import { useDebounce } from '../composables/useDebounce';

const { t } = useI18n();
const store = useCourseStore();

const searchQuery = ref('');
const delayedQuery = ref('');
const searchLoading = ref(false);
const selectedFilter = ref('all');
let searchTimer = null;

// Debounce watcher with delay
watch(searchQuery, (newVal) => {
  searchLoading.value = true;
  if (searchTimer) clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    delayedQuery.value = newVal;
    searchLoading.value = false;
  }, 500);
});

// Computed with delayed query and filter
const filteredCourses = computed(() => {
  const query = delayedQuery.value.toLowerCase().trim();
  let filtered = store.courses.filter((course) =>
    course.title.toLowerCase().includes(query)
  );
  if (selectedFilter.value !== 'all') {
    filtered = filtered.filter((course) =>
      course.level?.toLowerCase() === selectedFilter.value.toLowerCase()
    );
  }
  return filtered;
});

// Fetch courses when mounted
onMounted(() => {
  store.fetchCourses();
});
</script>

<style lang="css" scoped>
/* Empty style block to satisfy Vue's scoped requirement */
</style>