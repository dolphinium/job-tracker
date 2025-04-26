import api from "@/services/api";

export default {
  namespaced: true,
  state: {
    applications: [],
    currentApplication: null,
    loading: false,
    error: null,
  },
  getters: {
    applications: (state) => state.applications,
    currentApplication: (state) => state.currentApplication,
    applicationsByStatus: (state) => {
      const grouped = {};
      state.applications.forEach((app) => {
        if (!grouped[app.status]) {
          grouped[app.status] = [];
        }
        grouped[app.status].push(app);
      });
      return grouped;
    },
  },
  mutations: {
    SET_APPLICATIONS(state, applications) {
      state.applications = applications;
    },
    SET_CURRENT_APPLICATION(state, application) {
      state.currentApplication = application;
    },
    ADD_APPLICATION(state, application) {
      state.applications.push(application);
    },
    UPDATE_APPLICATION(state, updatedApplication) {
      const index = state.applications.findIndex(
        (a) => a.id === updatedApplication.id
      );
      if (index !== -1) {
        state.applications.splice(index, 1, updatedApplication);
      }
    },
    REMOVE_APPLICATION(state, id) {
      state.applications = state.applications.filter((a) => a.id !== id);
    },
    SET_LOADING(state, loading) {
      state.loading = loading;
    },
    SET_ERROR(state, error) {
      state.error = error;
    },
  },
  actions: {
    async fetchApplications({ commit }) {
      commit("SET_LOADING", true);
      try {
        const response = await api.getApplications();
        commit("SET_APPLICATIONS", response.data);
      } catch (error) {
        commit(
          "SET_ERROR",
          error.response?.data?.detail || "Failed to fetch applications"
        );
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async fetchApplication({ commit }, id) {
      commit("SET_LOADING", true);
      try {
        const response = await api.getApplication(id);
        commit("SET_CURRENT_APPLICATION", response.data);
      } catch (error) {
        commit(
          "SET_ERROR",
          error.response?.data?.detail || "Failed to fetch application"
        );
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async createApplication({ commit }, applicationData) {
      commit("SET_LOADING", true);
      try {
        const response = await api.createApplication(applicationData);
        commit("ADD_APPLICATION", response.data);
        return response.data;
      } catch (error) {
        commit(
          "SET_ERROR",
          error.response?.data?.detail || "Failed to create application"
        );
        throw error;
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async updateApplication({ commit }, { id, data }) {
      commit("SET_LOADING", true);
      try {
        const response = await api.updateApplication(id, data);
        commit("UPDATE_APPLICATION", response.data);
        return response.data;
      } catch (error) {
        commit(
          "SET_ERROR",
          error.response?.data?.detail || "Failed to update application"
        );
        throw error;
      } finally {
        commit("SET_LOADING", false);
      }
    },

    async deleteApplication({ commit }, id) {
      commit("SET_LOADING", true);
      try {
        await api.deleteApplication(id);
        commit("REMOVE_APPLICATION", id);
      } catch (error) {
        commit(
          "SET_ERROR",
          error.response?.data?.detail || "Failed to delete application"
        );
        throw error;
      } finally {
        commit("SET_LOADING", false);
      }
    },
  },
};
