import api from "@/services/api";
import router from "@/router";

export default {
  namespaced: true,
  state: {
    token: localStorage.getItem("token") || "",
    user: null,
    loading: false,
    error: null,
  },
  getters: {
    isAuthenticated: (state) => !!state.token,
    user: (state) => state.user,
  },
  mutations: {
    SET_TOKEN(state, token) {
      state.token = token;
    },
    SET_USER(state, user) {
      state.user = user;
    },
    SET_LOADING(state, loading) {
      state.loading = loading;
    },
    SET_ERROR(state, error) {
      state.error = error;
    },
    LOGOUT(state) {
      state.token = "";
      state.user = null;
    },
  },
  actions: {
    async login({ commit }, credentials) {
      commit("SET_LOADING", true);
      commit("SET_ERROR", null);
      try {
        // We're now handling form data directly in the API service
        const response = await api.login(credentials);
        const token = response.data.access_token;

        localStorage.setItem("token", token);
        commit("SET_TOKEN", token);

        // Get user profile
        const userResponse = await api.getProfile();
        commit("SET_USER", userResponse.data);

        router.push("/");
      } catch (error) {
        console.error("Login error:", error.response?.data || error.message);
        commit("SET_ERROR", error.response?.data?.detail || "Login failed");
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async register({ commit }, userData) {
      commit("SET_LOADING", true);
      commit("SET_ERROR", null);
      try {
        await api.register(userData);
        router.push("/login");
      } catch (error) {
        commit(
          "SET_ERROR",
          error.response?.data?.detail || "Registration failed"
        );
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async fetchUser({ commit }) {
      if (!localStorage.getItem("token")) return;

      commit("SET_LOADING", true);
      try {
        const response = await api.getProfile();
        commit("SET_USER", response.data);
      } catch (error) {
        commit(
          "SET_ERROR",
          error.response?.data?.detail || "Failed to fetch user"
        );
        // If token is invalid, logout
        if (error.response?.status === 401) {
          this.dispatch("auth/logout");
        }
      } finally {
        commit("SET_LOADING", false);
      }
    },

    logout({ commit }) {
      localStorage.removeItem("token");
      commit("LOGOUT");
      router.push("/login");
    },
  },
};
