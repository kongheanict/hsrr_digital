<template>
  <router-link :to="`/courses/${course.id}`" class="course-card">
    
    <div v-if="course.is_completed" class="completed">
      <i class="fa-solid fa-square-check"></i>
    </div>
    <div class="title-box">
      <img
        v-if="course.cover_image"
        :src="course.cover_image"
        :alt="course.title"
        class="cover-image"
      />
      <div class="course-info">
        <h3>{{ course.title }}</h3>
      </div>
    </div>
    
    <p>{{ course.description }}</p>
    <div class="complete-block">
      <button v-if="!course.is_completed" @click="$emit('complete')" class="complete-button">
        {{ $t('ចុចបញ្ជាក់ថាបានចប់') }}
      </button>
    </div>
  </router-link>
</template>

<script setup>
import { defineProps } from 'vue';

defineProps({
  course: Object,
});
defineEmits(['complete']);
</script>

<style lang="scss" scoped>
.course-card {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0.4, 0.3, 0.3, 0.3);
  text-decoration: none;
  color: #333;
  transition: transform 0.2s;
  p{
    font-size: 13px;
  }
}

.course-card:hover {
  transform: translateY(-5px);
}

.title-box{
  display: flex;
  gap: 10px;
  .cover-image {
    height: 35px;
    object-fit: cover;
    border-radius: 8px 8px 0 0;
    margin-bottom: 10px;
  }
}
.complete-block{
  position: relative;
  display: flex;
  justify-content: end;

}

.completed {
  display: flex;
  justify-content: end;
  i{
    color: #218838;
  }
}

.complete-button {
  position: relative;
  top: 0;
  background: #1a67cc;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

.complete-button:hover {
  background: #218838;
}


.course-info {
  flex: 1;
}

.course-info h3 {
  margin: 0 0 10px;
  font-size: 18px;
}

.course-info p {
  margin: 0;
  color: #666;
}
</style>