<template>
  <div class="flex py-10 md:py-0 min-h-screen max-w-7xl mx-auto">
    <CourseSidebar :isCourseSidebarVisible="isCourseSidebarVisible" @toggle-sidebar="toggleCourseSidebar" />
    <transition name="dimmer">
      <div v-if="isCourseSidebarVisible && isMobile" class="fixed inset-0 bg-opacity-50 z-20" @click="toggleCourseSidebar"></div>
    </transition>
    <div class="flex-1 p-4 md:p-6 lg:p-8 overflow-y-auto transition-all duration-300 relative md:ml-72" :class="{ 'ml-0': isCourseSidebarVisible || !isMobile }">
      <!-- Toggle button for sm screens -->
      <button v-if="isMobile" @click="toggleCourseSidebar">
        <svg v-if="!isCourseSidebarVisible" class="h-8 w-8 fixed bottom-20 right-4 p-2 bg-gray-300 rounded-full cursor-pointer hover:bg-gray-400 z-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
        <svg v-else class="h-8 w-8 fixed bottom-20 right-4 p-2 bg-gray-300 rounded-full cursor-pointer hover:bg-gray-400 z-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
      <div v-if="store.loading">
        <LoadingSpinner :show="store.loading" :text="$t('loading')" />
        <p>Page content goes here...</p>
      </div>
      <div v-else-if="store.error" class="text-red-500 text-center">{{ $t('error') }}: {{ store.error }}</div>
      <div v-else>
        <!-- Course and Lesson Titles -->
        <div class="border border-dashed border-blue-500 p-2 mb-6 text-center">
          <h2 class="text-lg md:text-2xl font-semibold text-gray-800 text-center mb-2">{{ store.currentCourse?.title }}</h2>
          <h3 v-if="currentLesson" class="text-sm md:text-xl text-gray-600 mt-4">{{ currentLesson.title }}</h3>
        </div>
        <div
          v-for="lesson in store.currentCourse?.lessons"
          :key="lesson.id"
          class="lesson mb-6"
          v-show="lesson.parts.some(part => part.id === store.selectedPartId)"
        >
          <div
            v-for="part in lesson.parts"
            :key="part.id"
            class="lesson-part bg-white p-2 md:p-6 border border-gray-200 border-t-0"
            :id="`part-${part.id}`"
            v-show="store.selectedPartId === part.id"
          >
            <h4 class="text-sm w-full rounded-sm bg-blue-500 p-2 md:text-lg font-bold text-white mb-4">{{ part.title }}</h4>
            <div
              class="part-content text-sm md:text-base text-gray-700 leading-relaxed"
              v-html="sanitizedContent(part.content)"
              @contextmenu.prevent
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useCourseStore } from '../stores/course';
import DOMPurify from 'dompurify';
import CourseSidebar from '../components/CourseSidebar.vue';
import LoadingSpinner from '../components/LoadingSpinner.vue';

const route = useRoute();
const store = useCourseStore();
const { t } = useI18n();

const isMobile = ref(window.innerWidth <= 768);
const isCourseSidebarVisible = ref(!isMobile.value);

const updateIsMobile = () => {
  const newMobile = window.innerWidth <= 768;
  if (newMobile !== isMobile.value) {
    isMobile.value = newMobile;
    isCourseSidebarVisible.value = !newMobile;
  }
};

// Compute current lesson based on selected part
const currentLesson = computed(() => {
  return store.currentCourse?.lessons.find(lesson =>
    lesson.parts.some(part => part.id === store.selectedPartId)
  );
});

// Sanitizer allowing iframe
const sanitizedContent = (content) =>
  DOMPurify.sanitize(content, {
    ADD_TAGS: ['iframe'],
    ADD_ATTR: [
      'allow',
      'allowfullscreen',
      'frameborder',
      'height',
      'width',
      'src',
      'title',
      'referrerpolicy'
    ],
    FORBID_ATTR: ['sandbox']
  });

const toggleCourseSidebar = () => {
  if (isMobile.value) {
    isCourseSidebarVisible.value = !isCourseSidebarVisible.value;
  }
};

// Lazy-load iframe
const observer = ref(null);
onMounted(() => {
  observer.value = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const iframe = entry.target.querySelector('iframe');
          if (iframe && !iframe.src && iframe.dataset.src) {
            iframe.src = iframe.dataset.src;
          }
        }
      });
    },
    { threshold: 0.1 }
  );
  document.querySelectorAll('.part-content').forEach((el) =>
    observer.value.observe(el)
  );

  window.addEventListener('resize', updateIsMobile);
  updateIsMobile(); // Initial check
});

onUnmounted(() => {
  observer.value?.disconnect();
  window.removeEventListener('resize', updateIsMobile);
});

onMounted(() => {
  store.fetchCourse(route.params.id);
});
</script>

<style lang="css" scoped>
.part-content {
  position: relative;
}

.part-content :deep(img) {
  @apply max-w-full h-auto rounded-md my-4;
}

.part-content :deep(iframe),
.part-content :deep(p iframe) {
  @apply w-full max-w-2xl h-80 border-none my-4 mx-auto block;
}

.part-content :deep(a) {
  @apply text-blue-600 no-underline hover:underline;
}

.dimmer-enter-active,
.dimmer-leave-active {
  transition: opacity 0.3s ease;
}

.dimmer-enter-from,
.dimmer-leave-to {
  opacity: 0;
}
</style>