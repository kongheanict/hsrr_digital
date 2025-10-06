<template>
  <div class="course-sidebar pt-5 md:pt-0 fixed left-0 w-72 border-r border-gray-200 bg-white h-screen overflow-y-auto transition-transform duration-300 z-30"
       :class="{ 'translate-x-[-100%]': !isCourseSidebarVisible }">
    <div class="sidebar-header flex justify-between items-center p-4 ">
      <h2 class="text-lg font-semibold text-gray-800">{{ store.currentCourse?.title || $t('loading') }}</h2>
    </div>
    <div class="parts-list p-4">
      <div v-for="lesson in store.currentCourse?.lessons" :key="lesson.id" class="lesson-group mb-4">
        <h4 @click="toggleLesson(lesson.id)"
            class="lesson-title flex gap-2 items-center py-2 bg-blue-50 pl-2 cursor-pointer hover:bg-gray-100 select-none text-sm font-medium text-gray-700">
            <span class="transition-transform duration-200">{{ expandedLessons[lesson.id] ? '▾' : '▸' }}</span>
          {{ lesson.title }}
        </h4>
        <ul v-if="expandedLessons[lesson.id]" class="space-y-1">
          <li v-for="part in lesson.parts" :key="part.id"
           @click.prevent="selectPart(part.id);">
            <a
              href="#"
              class="block px-4 py-2 text-xs md:text-md hover:bg-gray-100 cursor-pointer"
              :class="{ 'text-blue-600 font-semibold': store.selectedPartId === part.id }"
            >
              {{ part.title }}
            </a>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useCourseStore } from '../stores/course';
import { debounce } from 'lodash-es';

defineEmits(['toggle-sidebar']);
defineProps({
  isCourseSidebarVisible: Boolean,
});

const { t } = useI18n();
const store = useCourseStore();
const expandedLessons = ref({});

const isMobile = computed(() => window.innerWidth <= 768);

const toggleLesson = (lessonId) => {
  expandedLessons.value[lessonId] = !expandedLessons.value[lessonId];
};

const selectPart = debounce((partId) => {
  store.setSelectedPart(partId);
  const element = document.getElementById(`part-${partId}`);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' });
  }
}, 200);
</script>