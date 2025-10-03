<template>
  <div class="flex flex-col items-center justify-center min-h-screen bg-gray-50 px-4">
    <!-- Icon -->
    <div class="bg-red-100 p-6 rounded-full shadow-md">
      <svg xmlns="http://www.w3.org/2000/svg" 
           class="h-16 w-16 text-red-600" 
           fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    </div>

    <!-- Title -->
    <h1 class="mt-6 text-3xl font-bold text-red-600">ទទួលមិនបាន</h1>
    <p class="mt-2 text-gray-600 text-lg">
      អ្នកមិនមានសិទ្ធិចូលប្រើទំព័រនេះទេ។  
    </p>

    <!-- Suggestion -->
    <p class="mt-2 text-gray-500 text-sm">
      សូមទាក់ទងអ្នកគ្រប់គ្រងប្រសិនបើអ្នកគិតថាវាជាកំហុស។  
    </p>

    <!-- Back button -->
    <router-link 
      to="/" 
      class="mt-6 inline-flex items-center px-6 py-3 text-white bg-red-600 rounded-xl shadow hover:bg-red-700 transition">
      ⬅️ ត្រឡប់ទៅទំព័រដើម
    </router-link>
  </div>
</template>
