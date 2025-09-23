<template>
  <div class="flex">
    <!-- Only show sidebar when course is loaded -->
    <CourseSidebar
      v-if="course && course.lessons"
      :course="course"
      v-model:open="sidebarOpen"
      :selectedPartId="selectedPartId"
      @select-part="selectedPartId = $event"
    />

    <!-- Only show details when course is loaded -->
    <CourseDetail
      v-if="course && course.lessons"
      :course="course"
      :selectedPartId="selectedPartId"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCourseStore } from '../stores/course'
import CourseSidebar from './CourseSidebar.vue'
import CourseDetail from '../views/CourseDetail.vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const courseStore = useCourseStore()
const course = ref(null)
const sidebarOpen = ref(true)
const selectedPartId = ref(null)

onMounted(async () => {
  try {
    course.value = await courseStore.fetchCourse(route.params.id)
    // Only set selectedPartId if lessons exist
    if (course.value && course.value.lessons && course.value.lessons.length > 0) {
      selectedPartId.value = course.value.lessons[0].id
    }
  } catch (err) {
    console.error('Failed to load course:', err)
  }
})
</script>
