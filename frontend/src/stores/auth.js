// src/stores/auth.js
import { defineStore } from "pinia";
import axios from "axios";
import { jwtDecode } from "jwt-decode"; // ✅ modern named import

const API_URL = import.meta.env.VITE_API_URL;

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: JSON.parse(localStorage.getItem("user")) || null,
    accessToken: localStorage.getItem("access_token") || null,
    refreshToken: localStorage.getItem("refresh_token") || null,
    lastValidated: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    getUser: (state) => state.user,
  },

  actions: {
    login({ user, access, refresh }) {
      this.user = user;
      this.accessToken = access;
      this.refreshToken = refresh;
      this.lastValidated = Date.now();
      localStorage.setItem("user", JSON.stringify(user));
      localStorage.setItem("access_token", access);
      localStorage.setItem("refresh_token", refresh);
    },

    logout() {
      this.user = null;
      this.accessToken = null;
      this.refreshToken = null;
      this.lastValidated = null;
      localStorage.removeItem("user");
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      // window.location.href = "/login"; // force redirect to login
    },

    async refreshAccessToken() {
      if (!this.refreshToken) {
        this.logout();
        return null;
      }
      try {
        const response = await axios.post(`${API_URL}/token/refresh/`, {
          refresh: this.refreshToken,
        });
        this.accessToken = response.data.access;
        this.lastValidated = Date.now();
        localStorage.setItem("access_token", this.accessToken);
        return this.accessToken;
      } catch (err) {
        this.logout();
        return null;
      }
    },

    async validateToken() {
      if (!this.accessToken) return null;
      try {
        const { exp } = jwtDecode(this.accessToken);
        const now = Date.now() / 1000;
        if (exp < now) return await this.refreshAccessToken();
        return this.accessToken;
      } catch {
        return await this.refreshAccessToken();
      }
    },
  },
});

// Axios instance with interceptors
export const api = axios.create({
  baseURL: API_URL,
});

// Attach token to requests
api.interceptors.request.use((config) => {
  const store = useAuthStore();
  if (store.accessToken) config.headers.Authorization = `Bearer ${store.accessToken}`;
  return config;
});

// Refresh token automatically on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const store = useAuthStore();
    if (error.response?.status === 401) {
      const newAccess = await store.refreshAccessToken();
      if (newAccess) {
        error.config.headers.Authorization = `Bearer ${newAccess}`;
        return api.request(error.config);
      }
      store.logout();
    }
    return Promise.reject(error);
  }
);
