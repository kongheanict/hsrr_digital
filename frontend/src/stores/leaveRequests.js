import { defineStore } from 'pinia';
import { api, useAuthStore } from './auth';

export const useLeaveRequestsStore = defineStore('leaveRequests', {
  state: () => ({
    requests: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetchRequests() {
      this.loading = true;
      this.error = null;
      try {
        const authStore = useAuthStore();
        if (!authStore.isAuthenticated) {
          this.error = 'មិនទាន់បានចូល';
          return;
        }
        const token = await authStore.validateToken();
        if (!token) {
          this.error = 'សំគាល់សំងាត់មិនត្រឹមត្រូវ';
          return;
        }
        const response = await api.get('/teachers/leave-requests/');
        this.requests = response.data;
      } catch (err) {
        console.error('Fetch leave requests error:', err.response?.data || err.message);
        this.error = 'មិនអាចទាញសំណើបាន';
      } finally {
        this.loading = false;
      }
    },

    async submitRequest(formData) {
      this.loading = true;
      this.error = null;
      try {
        const authStore = useAuthStore();
        if (!authStore.isAuthenticated) {
          this.error = 'មិនទាន់បានចូល';
          return;
        }
        const token = await authStore.validateToken();
        if (!token) {
          this.error = 'សំគាល់សំងាត់មិនត្រឹមត្រូវ';
          return;
        }

        const response = await api.post('/teachers/leave-requests/', formData);

        // Make sure requests is an array
        if (!Array.isArray(this.requests)) {
          this.requests = [];
        }

        // Add the newly created request to the top
        this.requests.unshift(response.data);

        return response.data;

      } catch (err) {
        console.error('Submit leave request error:', err.response?.data || err.message);
        this.error = err.response?.data?.detail || 'កំហុសក្នុងការដាក់សំណើ';
      } finally {
        this.loading = false;
      }
    }

  },
});
