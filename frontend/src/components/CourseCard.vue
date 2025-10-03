<template>
  <div class="bg-white rounded-sm shadow-md hover:shadow-lg transition-all duration-300 flex flex-col h-full p-3 gap-2">
    <!-- Course Badge/Image -->
    <div class="flex gap-1 md:gap-4">
      <div class="relative w-24 h-24 shadow rounded-sm flex justify-center overflow-hidden">
        <img
          v-if="course.cover_image"
          :src="course.cover_image"
          :alt="course.title"
          class="w-full h-full object-contain"
        />
        <img
          v-else
          src="../assets/images/no-image.png"
          :alt="course.title"
          class="w-full h-full object-contain"
          />
        <div v-if="course.is_completed" class="absolute -top-1 -right-1 bg-green-600 text-white text-xs font-semibold px-1.5 py-0.5 rounded-bl-lg">
          {{ $t('រៀនចប់') }}
        </div>
      </div>
      <!-- Course Details -->
      <div class="flex-1 flex flex-col justify-between p-1">
        <!-- Title and Price -->
        <div class="flex justify-between items-start mb-1">
          <h3 class="text-md font-semibold text-gray-900 line-clamp-2">{{ course.title }}</h3>
          <span class="text-sm font-medium text-gray-600">{{ course.price || 'Free' }}</span>
        </div>
        <!-- Description -->
        <p class="text-sm text-gray-600 line-clamp-2">{{ course.description || $t('no_description') }}</p>
        <!-- Rating, Duration, and Button -->
        <div class="flex flex-col sm:flex-row justify-start md:justify-between items-start md:items-center gap-2 mt-2">
          <div class="flex gap-2 text-sm text-gray-500 ">
            <span class="flex items-start md:items-center">
              <svg class="w-4 h-4 text-yellow-400 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.539 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.381-1.81.588-1.81h3.461a1 1 0 00.95-.69l1.07-3.292z"/>
              </svg>
              {{ course.rating || '5.0' }}
            </span>
            <span class="">{{ course.duration || '15 Jul - 17 Aug' }}</span>
          </div>
          <router-link :to="`/courses/${course.id}`" class="w-full sm:w-auto hidden sm:block">
            <button
              class="w-full px-3 py-1 bg-indigo-600 text-white text-sm font-medium rounded-sm hover:bg-indigo-700 transition duration-200 cursor-pointer"
            >
              {{ $t('ចូលអានមេរៀន') }}
            </button>
          </router-link>
        </div>
      </div>
    </div>
    <router-link :to="`/courses/${course.id}`" class="w-full sm:w-auto sm:hidden mt-2">
          <button
            class="w-full px-3 py-1 bg-indigo-600 text-white text-sm font-medium rounded-sm hover:bg-indigo-700 transition duration-200 cursor-pointer"
          >
            {{ $t('ចូលអានមេរៀន') }}
          </button>
        </router-link>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

defineProps({
  course: {
    type: Object,
    required: true,
  },
});

defineEmits(['complete']);
</script>