import axios from "axios";

const apiClient = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for API calls
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default {
  // Auth services
  register(userData) {
    return apiClient.post("/auth/register", userData);
  },
  login(credentials) {
    const formData = new URLSearchParams();
    formData.append("username", credentials.email);
    formData.append("password", credentials.password);
    formData.append("grant_type", "password");

    return apiClient.post("/auth/login", formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
  },
  getProfile() {
    return apiClient.get("/auth/me");
  },

  // Application services
  getApplications() {
    return apiClient.get("/applications/");
  },
  getApplication(id) {
    return apiClient.get(`/applications/${id}`);
  },
  createApplication(application) {
    return apiClient.post("/applications/", application);
  },
  updateApplication(id, data) {
    return apiClient.put(`/applications/${id}`, data);
  },
  deleteApplication(id) {
    return apiClient.delete(`/applications/${id}`);
  },
  generateEmail(applicationId, data) {
    return apiClient.post(
      `/applications/${applicationId}/generate_email`,
      data
    );
  },
  suggestProjects(applicationId) {
    return apiClient.get(`/applications/${applicationId}/suggest_projects`);
  },

  // GitHub services
  fetchGitHubProjects(username, token = null) {
    const data = { username };
    if (token) {
      data.token = token;
    }
    return apiClient.post("/github/fetch", data);
  },
  getGitHubProjects() {
    return apiClient.get("/github/");
  },
  getGitHubRateLimit(token = null) {
    const params = token ? { token } : {};
    return apiClient.get("/github/rate-limit", { params });
  },
};
