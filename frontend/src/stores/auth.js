import { defineStore } from "pinia";
import axios from "axios";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: null,
    user: null,
  }),
  actions: {
    async login(username, password) {
      const response = await axios.post("/api/token/", { username, password });
      this.token = response.data.access;
      axios.defaults.headers.common["Authorization"] = `Bearer ${this.token}`;
    },
    logout() {
      this.token = null;
      this.user = null;
      delete axios.defaults.headers.common["Authorization"];
    },
  },
});
