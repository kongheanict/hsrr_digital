<template>
  <div class="min-h-screen max-w-3xl mx-auto px-6 py-18 md:py-8 bg-white rounded-xl shadow-lg">
    <!-- Header -->
    <h2 class="text-2xl font-bold mb-6 text-gray-800">សំណើឈប់សម្រាក</h2>

    <!-- Form -->
    <form @submit.prevent="submitForm" class="space-y-5">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">កាលបរិច្ឆេទចាប់ផ្តើម</label>
          <input 
            v-model="form.start_date" 
            type="date" 
            required 
            class="w-full px-3 py-2 border border-gray-300 rounded-sm focus:outline-none focus:ring-2 focus:ring-blue-400" 
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">កាលបរិច្ឆេទបញ្ចប់</label>
          <input 
            v-model="form.end_date" 
            type="date" 
            required 
            class="w-full px-3 py-2 border border-gray-300 rounded-sm focus:outline-none focus:ring-2 focus:ring-blue-400" 
          />
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">ហេតុផល</label>
        <textarea 
          v-model="form.reason" 
          rows="4" 
          required 
          placeholder="ពន្យល់ពីហេតុផល..."
          class="w-full p-3 border border-gray-300 rounded-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
        ></textarea>
      </div>

      <button 
        type="submit" 
        :disabled="loading" 
        class="w-full md:w-auto bg-blue-600 text-white px-6 py-3 rounded-sm font-semibold hover:bg-blue-700 transition disabled:opacity-50"
      >
        {{ loading ? 'កំពុងដាក់...' : 'ដាក់សំណើ' }}
      </button>

      <!-- Error Message -->
      <div v-if="error" class="mt-4 p-3 bg-red-100 text-red-700 rounded-sm font-medium">{{ error }}</div>
    </form>

    <!-- Previous Requests -->
    <div v-if="requests.length" class="mt-8">
      <h3 class="text-xl font-semibold mb-4 text-gray-700">សំណើមុនៗ</h3>
      <ul class="space-y-3">
        <li 
          v-for="req in requests" 
          :key="req.id" 
          class="p-4 border border-gray-200 rounded-xl flex justify-between items-center bg-gray-50"
        >
          <div>
            <p class="font-medium text-gray-800">
              {{ req.start_date }} ដល់ {{ req.end_date }}
            </p>
            <p class="text-gray-600 text-sm">{{ req.reason }}</p>
          </div>
          <span 
            class="px-3 py-1 rounded-full text-sm font-medium"
            :class="{
              'bg-green-100 text-green-800': req.status === 'Approved',
              'bg-yellow-100 text-yellow-800': req.status === 'Pending',
              'bg-red-100 text-red-800': req.status === 'Rejected'
            }"
          >
            {{ req.status }}
          </span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useLeaveRequestsStore } from '../../stores/leaveRequests';

const store = useLeaveRequestsStore();
const form = ref({
  start_date: '',
  end_date: '',
  reason: ''
});

const { requests, loading, error, fetchRequests, submitRequest } = store;

onMounted(() => {
  fetchRequests();
});

const submitForm = async () => {
  const result = await submitRequest(form.value);
  if (result) {
    form.value.start_date = '';
    form.value.end_date = '';
    form.value.reason = '';
  }
};
</script>
