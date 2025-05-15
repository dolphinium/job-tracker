import api from "@/services/api";

export default {
  namespaced: true,
  state: {
    applications: [],
    currentApplication: null,
    loading: false,
    error: null,
    generatedEmail: null,
    emailGenerationLoading: false,
    emailGenerationError: null,
    suggestedProjects: [],
    projectSuggestionLoading: false,
    projectSuggestionError: null,
  },
  getters: {
    applications: (state) => state.applications,
    currentApplication: (state) => state.currentApplication,
    generatedEmail: (state) => state.generatedEmail,
    emailGenerationLoading: (state) => state.emailGenerationLoading,
    emailGenerationError: (state) => state.emailGenerationError,
    suggestedProjects: (state) => state.suggestedProjects,
    projectSuggestionLoading: (state) => state.projectSuggestionLoading,
    projectSuggestionError: (state) => state.projectSuggestionError,
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
    SET_GENERATED_EMAIL(state, email) {
      state.generatedEmail = email;
    },
    SET_EMAIL_GENERATION_LOADING(state, loading) {
      state.emailGenerationLoading = loading;
    },
    SET_EMAIL_GENERATION_ERROR(state, error) {
      state.emailGenerationError = error;
    },
    SET_SUGGESTED_PROJECTS(state, projectIds) {
      state.suggestedProjects = projectIds;
    },
    SET_PROJECT_SUGGESTION_LOADING(state, loading) {
      state.projectSuggestionLoading = loading;
    },
    SET_PROJECT_SUGGESTION_ERROR(state, error) {
      state.projectSuggestionError = error;
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

    async generateEmail(
      { commit },
      { applicationId, projectIds, language = "english" }
    ) {
      commit("SET_EMAIL_GENERATION_LOADING", true);
      commit("SET_EMAIL_GENERATION_ERROR", null);
      commit("SET_GENERATED_EMAIL", null);

      try {
        const response = await api.generateEmail(applicationId, {
          project_ids: projectIds,
          language: language,
        });

        commit("SET_GENERATED_EMAIL", response.data.email_text);
        return response.data.email_text;
      } catch (error) {
        const errorMessage =
          error.response?.data?.detail || "Failed to generate email";
        commit("SET_EMAIL_GENERATION_ERROR", errorMessage);
        throw error;
      } finally {
        commit("SET_EMAIL_GENERATION_LOADING", false);
      }
    },

    async suggestProjects({ commit }, applicationId) {
      commit("SET_PROJECT_SUGGESTION_LOADING", true);
      commit("SET_PROJECT_SUGGESTION_ERROR", null);
      commit("SET_SUGGESTED_PROJECTS", []);

      try {
        const response = await api.suggestProjects(applicationId);
        commit("SET_SUGGESTED_PROJECTS", response.data.suggested_project_ids);
        return response.data.suggested_project_ids;
      } catch (error) {
        const errorMessage =
          error.response?.data?.detail || "Failed to suggest projects";
        commit("SET_PROJECT_SUGGESTION_ERROR", errorMessage);
        throw error;
      } finally {
        commit("SET_PROJECT_SUGGESTION_LOADING", false);
      }
    },
  },
};
