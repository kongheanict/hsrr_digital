<template>
  <div class="flex-1 p-6">
    <h1 class="text-2xl font-bold mb-4">{{ course.title }}</h1>
    <p class="mb-6">{{ course.description }}</p>

    <div v-if="selectedLesson">
      <h2 class="text-xl font-semibold mb-2">{{ selectedLesson.title }}</h2>
      <div class="prose max-w-full">
        <p v-html="selectedLesson.content"></p>
      </div>
    </div>

    <div v-else class="text-gray-500">
      Select a lesson from the left sidebar
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  course: { type: Object, required: true },
  selectedPartId: { type: Number, required: true }
})

const selectedLesson = computed(() =>
  props.course.lessons.find((l) => l.id === props.selectedPartId)
)
</script>
