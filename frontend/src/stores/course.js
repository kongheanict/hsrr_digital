import { defineStore } from 'pinia';
import axios from 'axios';
import { useAuthStore } from './auth';

export const useCourseStore = defineStore('course', {
  state: () => ({
    courses: [],
    currentCourse: null,
    loading: false,
    error: null,
    selectedPartId: null,
    isCourseSidebarVisible: true,
  }),
  actions: {
    async fetchCourses() {
      if (this.courses.length > 0) {
        return; // already loaded
      }

      this.loading = true;
      try {
        
        const auth = useAuthStore();
        if (!auth.isAuthenticated) return;
        const response = await axios.get('/api/courses/', {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
        });
        this.courses = response.data;
      } catch (error) {
        this.error = error.response?.data?.detail || 'កំហុសក្នុងការទាញយកវគ្គសិក្សា';
      } finally {
        this.loading = false;
      }
    },
    async fetchCourse(id) {
      this.loading = true;
      try {
        
        const auth = useAuthStore();
        if (!auth.isAuthenticated) return;
        const response = await axios.get(`/api/courses/${id}/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
        });
        this.currentCourse = response.data;
        if (response.data?.lessons?.[0]?.parts?.[0]) {
          this.selectedPartId = response.data.lessons[0].parts[0].id;
        }
      } catch (error) {
        this.error = error.response?.data?.detail || 'កំហុសក្នុងការទាញយកវគ្គសិក្សា';
      } finally {
        this.loading = false;
      }
    },
    async completeCourse(courseId) {
      try {
        
        const auth = useAuthStore();
        if (!auth.isAuthenticated) return;
        const response = await axios.post('/api/courses/complete-course/', {
          course_id: courseId,
        }, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
        });
        const course = this.courses.find(c => c.id === courseId);
        if (course) course.is_completed = true;
        return response.data;
      } catch (error) {
        console.error('Course completion failed:', error);
      }
    },
    setSelectedPart(partId) {
      this.selectedPartId = partId;
    },
    toggleCourseSidebar() {
      this.isCourseSidebarVisible = !this.isCourseSidebarVisible;
    },
  },
});