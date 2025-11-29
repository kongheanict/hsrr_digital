<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-950 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
    <!-- Background Decoration -->
    <div class="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
        <div class="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-primary-500/20 blur-[120px] animate-pulse"></div>
        <div class="absolute top-[40%] -right-[10%] w-[40%] h-[40%] rounded-full bg-blue-500/20 blur-[100px] animate-pulse delay-1000"></div>
    </div>

    <UCard class="w-full max-w-md z-10 backdrop-blur-sm bg-white/80 dark:bg-gray-900/80 ring-1 ring-gray-200 dark:ring-gray-800 shadow-xl">
      <template #header>
        <div class="flex flex-col items-center space-y-2 py-4">
            <div class="p-3 bg-primary-50 dark:bg-primary-950/50 rounded-xl mb-2">
                <UIcon name="i-lucide-lock" class="w-8 h-8 text-primary-500" />
            </div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Welcome Back</h1>
            <p class="text-sm text-gray-500 dark:text-gray-400">Sign in to your account to continue</p>
        </div>
      </template>

      <!-- Error Alert -->
      <UAlert
        v-if="errorMessage"
        color="red"
        variant="soft"
        :title="errorMessage"
        icon="i-lucide-alert-circle"
        :close-button="{ icon: 'i-lucide-x', color: 'red', variant: 'link', padded: false }"
        @close="errorMessage = ''"
        class="mb-4"
      />

      <form @submit.prevent="login" class="space-y-6">
        <UFormGroup label="Username" name="username" required>
          <UInput 
            v-model="username" 
            icon="i-lucide-user" 
            placeholder="Enter your username" 
            size="lg"
            :ui="{ icon: { trailing: { pointer: '' } } }"
          />
        </UFormGroup>

        <UFormGroup label="Password" name="password" required>
          <UInput 
            v-model="password" 
            type="password" 
            icon="i-lucide-key" 
            placeholder="Enter your password" 
            size="lg"
          />
        </UFormGroup>

        <div class="flex items-center justify-between text-sm">
            <UCheckbox label="Remember me" />
            <a href="#" class="text-primary-500 hover:text-primary-600 font-medium transition-colors">Forgot password?</a>
        </div>

        <UButton 
            type="submit" 
            block 
            size="lg" 
            :loading="loading"
            class="font-semibold"
        >
            Sign In
        </UButton>
      </form>

      <template #footer>
        <p class="text-center text-sm text-gray-500 dark:text-gray-400">
            Don't have an account? 
            <a href="/register" class="text-primary-500 hover:text-primary-600 font-medium transition-colors">Create account</a>
        </p>
      </template>
    </UCard>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

const login = async () => {
    // Clear previous error
    errorMessage.value = ''

    if (!username.value || !password.value) {
        errorMessage.value = 'Please enter both username and password'
        return
    }

    loading.value = true
    try {
        const result = await authStore.login(username.value, password.value)
        
        if (result.success) {
            toast.add({
                title: 'Login Successful',
                description: 'Welcome back!',
                color: 'green',
            })
            router.push('/')
        } else {
            errorMessage.value = result.error || 'Invalid username or password'
        }
    } catch (error) {
        console.error(error)
        errorMessage.value = 'An unexpected error occurred. Please try again.'
    } finally {
        loading.value = false
    }
}
</script>
