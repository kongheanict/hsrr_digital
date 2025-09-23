<template>
  <div class="px-5 max-w-[1200px] mx-auto">
    <h1 class="text-2xl font-semibold text-gray-800 mb-6">{{ $t('courses') }}</h1>

    <!-- Search input -->
    <input
      v-model="searchQuery"
      type="text"
      :placeholder="$t('ស្វែងរកចំណងជើង...')"
      class="w-[328px] max-w-[400px] px-2.5 py-2 mb-5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
    />

    <!-- Show global loading from store -->
    <div v-if="store.loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-t-4 border-blue-500"></div>
      <p class="ml-4 text-lg text-gray-600">{{ $t('Loading quiz data...') }}</p>
    </div>
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-t-4 border-blue-500"></div>
      <p class="ml-4 text-lg text-gray-600">{{ $t('Loading quiz data...') }}</p>
    </div>

    <!-- Show local search debounce loading -->
    <div v-else-if="searchLoading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-t-4 border-blue-500"></div>
      <p class="ml-4 text-lg text-gray-600">{{ $t('Loading quiz data...') }}</p>
    </div>

    <!-- Error state -->
    <div v-else-if="store.error" class="text-center px-5 py-5 text-red-500">
      {{ $t('error') }}: {{ store.error }}
    </div>

    <!-- Results -->
    <div class="grid grid-cols-[repeat(auto-fill,_minmax(300px,_1fr))] gap-5">
      <CourseCard
        v-for="course in filteredCourses"
        :key="course.id"
        :course="course"
        @complete="store.completeCourse(course.id)"
      />
      <p v-if="filteredCourses.length === 0" class="text-center text-gray-600">{{ $t('មិនមានវគ្គសិក្សា') }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useCourseStore } from '../stores/course';
import CourseCard from '../components/CourseCard.vue';
import { useDebounce } from '../composables/useDebounce';
import LoadingSpinner from '../components/LoadingSpinner.vue';

const { t } = useI18n();
const store = useCourseStore();

const searchQuery = ref('');
const delayedQuery = ref('');
const searchLoading = ref(false);
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

// Computed with delayed query
const filteredCourses = computed(() => {
  const query = delayedQuery.value.toLowerCase().trim();
  return store.courses.filter((course) =>
    course.title.toLowerCase().includes(query)
  );
});

// Fetch courses when mounted
onMounted(() => {
  store.fetchCourses();
});
</script>

<style lang="css" scoped>
/* Empty style block to satisfy Vue's scoped requirement */
</style>