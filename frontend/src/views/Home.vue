<template>
  <div class="antialiased min-h-screen">
    <!-- Full-Screen Image Cover with Overlay -->
    <div
      class="relative h-screen bg-cover bg-center"
      style="background-image: url('https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?ixlib=rb-4.0.3&auto=format&fit=crop&w=1350&q=80')"
    >
      <div class="absolute inset-0 bg-gray-900 opacity-60"></div>
      <div class="relative z-10 h-full flex items-center justify-center">
        <div class="text-center px-6 py-12  bg-opacity-90 rounded-lg shadow-xl max-w-md">
          <p class="text-lg text-white mb-6">អោយតែមានចិត្តចង់រៀន ហើយបណ្ដុះភាពអំណត់ ក្នុងការនឿយហត់</p>
          <!-- <button
            @click="scrollToLogin"
            class="px-8 py-3 bg-indigo-600 text-white font-semibold rounded-md shadow-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition duration-150 ease-in-out"
          >
            ចាប់ផ្តើមរកផ្លូវ
          </button> -->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>



const scrollToLogin = () => {
  if (loginSection.value) {
    loginSection.value.scrollIntoView({ behavior: 'smooth' });
  }
};
</script>