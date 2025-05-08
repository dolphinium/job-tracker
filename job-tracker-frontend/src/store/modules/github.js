import api from "@/services/api";

export default {
  namespaced: true,
  state: {
    projects: [],
    username: localStorage.getItem("github_username") || "",
    loading: false,
    error: null,
    initialized: false,
    rateLimit: null,
  },
  getters: {
    projects: (state) => state.projects,
    username: (state) => state.username,
    hasUsername: (state) => !!state.username,
    initialized: (state) => state.initialized,
    rateLimit: (state) => state.rateLimit,
  },
  mutations: {
    SET_PROJECTS(state, projects) {
      state.projects = projects;
    },
    SET_USERNAME(state, username) {
      state.username = username;
      localStorage.setItem("github_username", username);
    },
    SET_LOADING(state, loading) {
      state.loading = loading;
    },
    SET_ERROR(state, error) {
      state.error = error;
    },
    SET_INITIALIZED(state, initialized) {
      state.initialized = initialized;
    },
    SET_RATE_LIMIT(state, rateLimit) {
      state.rateLimit = rateLimit;
    },
  },
  actions: {
    async fetchProjects(
      { commit, state },
      { username = null, token = null } = {}
    ) {
      // Use provided username or fall back to state
      const targetUsername = username || state.username;
      if (!targetUsername) {
        commit("SET_ERROR", "GitHub username not set");
        return [];
      }

      commit("SET_LOADING", true);
      commit("SET_ERROR", null);

      try {
        const response = await api.fetchGitHubProjects(targetUsername, token);
        commit("SET_PROJECTS", response.data);
        commit("SET_INITIALIZED", true);
        return response.data;
      } catch (error) {
        // Format error message from response
        let errorMessage = "Failed to fetch GitHub projects";

        if (error.response) {
          if (
            error.response.status === 429 ||
            (error.response.status === 403 &&
              error.response.data.detail &&
              error.response.data.detail.includes("rate limit"))
          ) {
            errorMessage =
              "GitHub API rate limit exceeded. Try again later or add a GitHub token.";
          } else if (error.response.data && error.response.data.detail) {
            errorMessage = error.response.data.detail;
          }
        }

        commit("SET_ERROR", errorMessage);
        throw error;
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async getProjects({ commit, state, dispatch }) {
      // If projects are already loaded and initialized, return them
      if (state.projects.length > 0 && state.initialized) {
        return state.projects;
      }

      // Otherwise, try to load from API
      commit("SET_LOADING", true);
      commit("SET_ERROR", null);

      try {
        const response = await api.getGitHubProjects();
        commit("SET_PROJECTS", response.data);
        commit("SET_INITIALIZED", true);
        return response.data;
      } catch (error) {
        // If API fails and we have a username, try fetching fresh data
        if (
          state.username &&
          (error.response?.status === 404 ||
            (error.response?.data?.detail &&
              error.response?.data?.detail.includes("No projects found")))
        ) {
          return dispatch("fetchProjects", { username: state.username });
        }

        // Don't set error if we're just initializing with no projects yet
        if (error.response && error.response.status !== 404) {
          let errorMessage = "Failed to get GitHub projects";

          if (error.response.data && error.response.data.detail) {
            errorMessage = error.response.data.detail;
          }

          commit("SET_ERROR", errorMessage);
        }

        return [];
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async getRateLimit({ commit }, token = null) {
      try {
        const response = await api.getGitHubRateLimit(token);
        const rateLimit = response.data;
        commit("SET_RATE_LIMIT", rateLimit);
        return rateLimit;
      } catch (error) {
        console.error("Failed to get rate limit info:", error);
        return null;
      }
    },

    setUsername({ commit }, username) {
      commit("SET_USERNAME", username);
    },
  },
};
