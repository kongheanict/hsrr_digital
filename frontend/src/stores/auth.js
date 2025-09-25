import { defineStore } from "pinia";
import axios from "axios";
import { jwtDecode } from "jwt-decode";

const API_URL = import.meta.env.VITE_API_URL;

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: JSON.parse(localStorage.getItem("user")) || null,
    accessToken: localStorage.getItem("access_token") || null,
    refreshToken: localStorage.getItem("refresh_token") || null,
    lastValidated: localStorage.getItem("last_validated") ? parseInt(localStorage.getItem("last_validated")) : null,
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
      localStorage.setItem("last_validated", this.lastValidated.toString());
    },

    logout() {
      this.user = null;
      this.accessToken = null;
      this.refreshToken = null;
      this.lastValidated = null;
      localStorage.removeItem("user");
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("last_validated");
    },

    async refreshAccessToken() {
      if (!this.refreshToken) {
        this.logout();
        return null;
      }
      try {
        const response = await axios.post(`${API_URL}token/refresh/`, {
          refresh: this.refreshToken,
        });
        this.accessToken = response.data.access;
        this.lastValidated = Date.now();
        localStorage.setItem("access_token", this.accessToken);
        localStorage.setItem("last_validated", this.lastValidated.toString());
        return this.accessToken;
      } catch (err) {
        console.error('Token refresh error:', err.response?.data || err.message);
        this.logout();
        return null;
      }
    },

    async validateToken() {
      if (!this.accessToken) return null;
      // Avoid refreshing if validated recently (e.g., within 1 minute)
      if (this.lastValidated && Date.now() - this.lastValidated < 60 * 1000) {
        return this.accessToken;
      }
      try {
        const { exp } = jwtDecode(this.accessToken);
        const now = Date.now() / 1000;
        if (exp < now) {
          return await this.refreshAccessToken();
        }
        this.lastValidated = Date.now();
        localStorage.setItem("last_validated", this.lastValidated.toString());
        return this.accessToken;
      } catch (err) {
        console.error('Token validation error:', err.message);
        return await this.refreshAccessToken();
      }
    },
  },
});

export const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  const store = useAuthStore();
  if (store.accessToken) config.headers.Authorization = `Bearer ${store.accessToken}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const store = useAuthStore();
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      const newAccess = await store.refreshAccessToken();
      if (newAccess) {
        error.config.headers.Authorization = `Bearer ${newAccess}`;
        return api.request(error.config);
      }
    }
    return Promise.reject(error);
  }
);