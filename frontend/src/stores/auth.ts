import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../lib/api'
import { jwtDecode } from 'jwt-decode'

interface User {
    username: string
    role?: string
    fullname?: string
}

interface JWTPayload {
    user_id: number
    username?: string
    role?: string
    fullname?: string
}

export const useAuthStore = defineStore('auth', () => {
    const user = ref<User | null>(null)
    const accessToken = ref<string | null>(null)
    const refreshToken = ref<string | null>(null)

    const isAuthenticated = computed(() => !!accessToken.value)

    // Initialize from localStorage
    const initAuth = () => {
        const storedAccess = localStorage.getItem('access_token')
        const storedRefresh = localStorage.getItem('refresh_token')

        if (storedAccess && storedRefresh) {
            accessToken.value = storedAccess
            refreshToken.value = storedRefresh

            try {
                const decoded = jwtDecode<JWTPayload>(storedAccess)
                user.value = {
                    username: decoded.username || '',
                    role: decoded.role,
                    fullname: decoded.fullname,
                }
            } catch (error) {
                console.error('Failed to decode token:', error)
                logout()
            }
        }
    }

    const login = async (username: string, password: string) => {
        try {
            const response = await api.post('/api/token/', {
                username,
                password,
            })

            const { access, refresh } = response.data

            // Store tokens
            accessToken.value = access
            refreshToken.value = refresh
            localStorage.setItem('access_token', access)
            localStorage.setItem('refresh_token', refresh)

            // Decode and store user info
            const decoded = jwtDecode<JWTPayload>(access)
            user.value = {
                username: decoded.username || username,
                role: decoded.role,
                fullname: decoded.fullname,
            }

            return { success: true }
        } catch (error: any) {
            console.error('Login failed:', error)
            return {
                success: false,
                error: error.response?.data?.detail || 'Invalid username or password',
            }
        }
    }

    const logout = () => {
        user.value = null
        accessToken.value = null
        refreshToken.value = null
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
    }

    return {
        user,
        accessToken,
        refreshToken,
        isAuthenticated,
        initAuth,
        login,
        logout,
    }
})
