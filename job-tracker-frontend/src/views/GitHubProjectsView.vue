<template>
  <main-layout>
    <v-card flat class="pa-0">
      <v-card-title
        class="d-flex flex-column flex-lg-row align-stretch align-lg-center pa-4"
      >
        <span class="text-h6 font-weight-regular mb-3 mb-lg-0 mr-lg-4"
          >GitHub Projects</span
        >
        <v-spacer class="d-none d-lg-block"></v-spacer>

        <div
          class="d-flex flex-column flex-sm-row align-stretch mt-2 mt-lg-0 w-100 w-lg-auto"
          style="gap: 12px"
        >
          <!-- GitHub Token Input -->
          <v-tooltip
            location="bottom"
            text="Personal Access Token increases API rate limits"
            class="flex-grow-1"
          >
            <template v-slot:activator="{ props }">
              <v-text-field
                v-model="tokenInput"
                label="GitHub Token (optional)"
                append-inner-icon="mdi-key-variant"
                hide-details
                density="compact"
                variant="outlined"
                type="password"
                v-bind="props"
                style="min-width: 220px"
              ></v-text-field>
            </template>
          </v-tooltip>

          <!-- GitHub Username Input -->
          <v-text-field
            v-model="usernameInput"
            label="GitHub Username"
            append-inner-icon="mdi-account"
            hide-details
            density="compact"
            variant="outlined"
            class="flex-grow-1"
            style="min-width: 200px"
            @keyup.enter="handleFetchProjects"
          ></v-text-field>

          <v-btn
            color="primary"
            :loading="loading"
            :disabled="!usernameInput"
            @click="handleFetchProjects"
            prepend-icon="mdi-refresh"
            variant="flat"
            class="flex-sm-grow-0"
            style="min-width: 180px"
          >
            {{ username ? "Refresh Projects" : "Fetch Projects" }}
          </v-btn>
        </div>
      </v-card-title>

      <v-divider></v-divider>

      <!-- Rate Limit Info -->
      <v-alert
        v-if="rateLimit"
        color="info"
        icon="mdi-information-outline"
        variant="tonal"
        class="ma-4"
        closable
      >
        <div class="d-flex align-center justify-space-between flex-wrap">
          <div>
            <strong>GitHub API Rate Limit:</strong> {{ rateLimit.remaining }} /
            {{ rateLimit.limit }} remaining
          </div>
          <div>
            <strong>Resets:</strong> {{ formatRateLimitReset(rateLimit.reset) }}
          </div>
          <div v-if="!tokenInput && rateLimit.remaining < 10">
            <v-btn
              color="info"
              size="small"
              variant="text"
              prepend-icon="mdi-key-variant"
              @click="showTokenInfo = true"
            >
              Add Token for Higher Limits
            </v-btn>
          </div>
        </div>
      </v-alert>

      <!-- Rate Limit Dialog -->
      <v-dialog v-model="showTokenInfo" max-width="600">
        <v-card>
          <v-card-title class="text-h6 pa-4">
            GitHub API Rate Limits
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text class="pa-4">
            <p class="mb-4">
              GitHub limits API requests to 60 per hour for unauthenticated
              requests. This can be increased to 5,000 requests per hour by
              using a personal access token.
            </p>
            <v-alert color="warning" variant="tonal" class="mb-4">
              <strong>Note:</strong> Your token will only be used for API
              requests and will not be stored on our server.
            </v-alert>
            <p>To create a personal access token:</p>
            <ol class="ml-4 mb-4">
              <li>
                Go to your GitHub
                <a href="https://github.com/settings/tokens" target="_blank"
                  >Personal Access Tokens</a
                >
                page
              </li>
              <li>Click "Generate new token" (classic)</li>
              <li>Give it a name (e.g., "Job Tracker")</li>
              <li>
                Select only the <strong>public_repo</strong> scope - no other
                permissions are needed
              </li>
              <li>Click "Generate token" and copy the token value</li>
            </ol>
            <v-text-field
              v-model="tokenInput"
              label="GitHub Personal Access Token"
              variant="outlined"
              type="password"
              hint="Paste your token here"
              persistent-hint
            ></v-text-field>
          </v-card-text>
          <v-divider></v-divider>
          <v-card-actions class="pa-4">
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              variant="text"
              @click="showTokenInfo = false"
            >
              Close
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Rate Limit Error -->
      <v-alert
        v-if="rateLimitError"
        color="error"
        icon="mdi-alert-circle"
        variant="tonal"
        class="ma-4"
      >
        <div class="mb-2"><strong>Rate Limit Exceeded</strong></div>
        <p>{{ rateLimitError.message }}</p>
        <div class="d-flex align-center mt-2">
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            size="small"
            prepend-icon="mdi-key-variant"
            variant="text"
            @click="showTokenInfo = true"
            class="mr-2"
          >
            Add Token
          </v-btn>
          <v-btn
            color="primary"
            size="small"
            prepend-icon="mdi-clock-outline"
            variant="flat"
            @click="checkRateLimit"
          >
            Check Status
          </v-btn>
        </div>
      </v-alert>

      <!-- No username message -->
      <v-card-text v-if="!username && !loading" class="text-center pa-8">
        <v-icon size="64" color="grey-lighten-1" class="mb-4"
          >mdi-github</v-icon
        >
        <h3 class="text-h6 mb-2">No GitHub Username Set</h3>
        <p class="text-body-1 text-grey-darken-1 mb-4">
          Enter your GitHub username above and click "Fetch Projects" to display
          your repositories.
        </p>
      </v-card-text>

      <!-- Error message -->
      <v-alert
        v-if="error && !rateLimitError"
        type="error"
        variant="tonal"
        closable
        class="ma-4"
      >
        {{ error }}
      </v-alert>

      <!-- Loading state -->
      <div v-if="loading" class="text-center pa-8">
        <v-progress-circular
          indeterminate
          color="primary"
          size="64"
        ></v-progress-circular>
        <div class="mt-4 text-body-1">Loading GitHub projects...</div>
      </div>

      <!-- Projects grid -->
      <v-container v-if="!loading && projects.length > 0" fluid class="pa-4">
        <v-row>
          <v-col
            v-for="project in projects"
            :key="project.id"
            cols="12"
            md="6"
            lg="4"
            xl="3"
          >
            <v-card variant="outlined" class="h-100 d-flex flex-column" hover>
              <v-card-item>
                <template v-slot:prepend>
                  <v-icon
                    :color="getLanguageColor(project.language)"
                    size="large"
                    class="mr-2"
                  >
                    mdi-source-repository
                  </v-icon>
                </template>

                <v-card-title class="pa-0 text-h6 font-weight-medium">
                  <a
                    :href="project.html_url"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-decoration-none"
                  >
                    {{ project.name }}
                  </a>
                </v-card-title>

                <template v-slot:append>
                  <v-chip
                    v-if="project.language"
                    size="small"
                    :color="getLanguageColor(project.language)"
                    variant="flat"
                  >
                    {{ project.language }}
                  </v-chip>
                </template>
              </v-card-item>

              <v-card-text class="flex-grow-1">
                <p v-if="project.description" class="text-body-1">
                  {{ project.description }}
                </p>
                <p v-else class="text-grey-darken-1 font-italic">
                  No description available
                </p>

                <div class="d-flex align-center mt-4">
                  <v-tooltip location="top" text="Stars">
                    <template v-slot:activator="{ props }">
                      <div class="d-flex align-center mr-4" v-bind="props">
                        <v-icon
                          size="small"
                          color="amber-darken-2"
                          class="mr-1"
                        >
                          mdi-star
                        </v-icon>
                        <span>{{ project.stars }}</span>
                      </div>
                    </template>
                  </v-tooltip>

                  <v-tooltip location="top" text="Forks">
                    <template v-slot:activator="{ props }">
                      <div class="d-flex align-center" v-bind="props">
                        <v-icon size="small" color="blue-grey" class="mr-1">
                          mdi-source-fork
                        </v-icon>
                        <span>{{ project.forks }}</span>
                      </div>
                    </template>
                  </v-tooltip>

                  <v-spacer></v-spacer>

                  <v-tooltip
                    v-if="project.last_commit_date"
                    location="top"
                    text="Last Commit"
                  >
                    <template v-slot:activator="{ props }">
                      <div
                        class="d-flex align-center text-caption text-grey-darken-1"
                        v-bind="props"
                      >
                        <v-icon size="small" class="mr-1"
                          >mdi-source-commit</v-icon
                        >
                        <span>{{ formatDate(project.last_commit_date) }}</span>
                      </div>
                    </template>
                  </v-tooltip>
                </div>
              </v-card-text>

              <v-divider v-if="project.readme_content"></v-divider>

              <v-expansion-panels v-if="project.readme_content">
                <v-expansion-panel>
                  <v-expansion-panel-title>
                    <div class="d-flex align-center">
                      <v-icon size="small" class="mr-2"
                        >mdi-file-document-outline</v-icon
                      >
                      <span>README.md</span>
                    </div>
                  </v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <div class="readme-content">
                      {{ truncateReadme(project.readme_content) }}
                    </div>
                    <div class="text-center mt-2">
                      <v-btn
                        color="primary"
                        variant="text"
                        :href="`${project.html_url}#readme`"
                        target="_blank"
                        rel="noopener noreferrer"
                        size="small"
                      >
                        View Full README
                      </v-btn>
                    </div>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>

              <v-card-actions>
                <v-btn
                  variant="flat"
                  color="primary"
                  :href="project.html_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  size="small"
                >
                  View Repository
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </v-container>

      <!-- No projects found message -->
      <v-card-text
        v-if="!loading && username && projects.length === 0 && !rateLimitError"
        class="text-center pa-8"
      >
        <v-icon size="64" color="grey-lighten-1" class="mb-4"
          >mdi-github</v-icon
        >
        <h3 class="text-h6 mb-2">No GitHub Projects Found</h3>
        <p class="text-body-1 text-grey-darken-1">
          No public repositories were found for the username "{{ username }}".
        </p>
      </v-card-text>
    </v-card>
  </main-layout>
</template>

<script>
import { mapState, mapGetters, mapActions } from "vuex";
import MainLayout from "@/layouts/MainLayout.vue";

export default {
  name: "GitHubProjectsView",
  components: {
    MainLayout,
  },
  data() {
    return {
      usernameInput: "",
      tokenInput: localStorage.getItem("github_token") || "",
      showTokenInfo: false,
      rateLimit: null,
      rateLimitError: null,
      languageColors: {
        JavaScript: "amber",
        TypeScript: "blue",
        Python: "green",
        Java: "red",
        HTML: "orange",
        CSS: "purple",
        Vue: "teal",
        "C#": "blue-darken-4",
        PHP: "indigo",
        Ruby: "red-darken-4",
        Go: "cyan",
        Rust: "deep-orange",
        Swift: "orange-darken-2",
        Kotlin: "purple-darken-1",
        // Add more languages as needed
      },
    };
  },
  computed: {
    ...mapState("github", ["projects", "loading", "error"]),
    ...mapGetters("github", ["username"]),
  },
  watch: {
    tokenInput(newVal) {
      // Save token to localStorage when it changes
      localStorage.setItem("github_token", newVal || "");
    },
  },
  methods: {
    ...mapActions("github", [
      "fetchProjects",
      "getProjects",
      "setUsername",
      "getRateLimit",
    ]),

    async handleFetchProjects() {
      if (!this.usernameInput) {
        return;
      }

      // Clear previous rate limit error
      this.rateLimitError = null;

      // Update username in store
      this.setUsername(this.usernameInput);

      try {
        // Pass token if available
        await this.fetchProjects({
          username: this.usernameInput,
          token: this.tokenInput,
        });
        // Check rate limit after fetch
        await this.checkRateLimit();
      } catch (error) {
        console.error("Error fetching GitHub projects:", error);

        // Handle rate limit errors
        if (error.response && error.response.status === 429) {
          const rateLimitInfo = error.response.data.detail.rate_limit;
          this.rateLimitError = {
            message: error.response.data.detail.message,
            reset: new Date(rateLimitInfo.reset),
            limit: rateLimitInfo.limit,
            remaining: rateLimitInfo.remaining,
          };
        }
      }
    },

    async checkRateLimit() {
      try {
        this.rateLimit = await this.getRateLimit(this.tokenInput);
      } catch (error) {
        console.error("Error checking rate limit:", error);
      }
    },

    formatDate(dateString) {
      if (!dateString) return "Unknown";

      const date = new Date(dateString);
      if (isNaN(date.getTime())) return "Invalid date";

      const now = new Date();
      const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));

      if (diffDays === 0) {
        return "Today";
      } else if (diffDays === 1) {
        return "Yesterday";
      } else if (diffDays < 7) {
        return `${diffDays} days ago`;
      } else if (diffDays < 30) {
        const weeks = Math.floor(diffDays / 7);
        return `${weeks} ${weeks === 1 ? "week" : "weeks"} ago`;
      } else if (diffDays < 365) {
        const months = Math.floor(diffDays / 30);
        return `${months} ${months === 1 ? "month" : "months"} ago`;
      } else {
        const years = Math.floor(diffDays / 365);
        return `${years} ${years === 1 ? "year" : "years"} ago`;
      }
    },

    formatRateLimitReset(resetTimeStr) {
      if (!resetTimeStr) return "Unknown";

      const resetTime = new Date(resetTimeStr);
      if (isNaN(resetTime.getTime())) return "Unknown";

      const now = new Date();
      const diffMinutes = Math.floor((resetTime - now) / (1000 * 60));

      if (diffMinutes < 0) {
        return "Reset time passed";
      } else if (diffMinutes < 1) {
        return "Less than a minute";
      } else if (diffMinutes < 60) {
        return `${diffMinutes} minutes`;
      } else {
        const hours = Math.floor(diffMinutes / 60);
        const mins = diffMinutes % 60;
        return `${hours}h ${mins}m`;
      }
    },

    getLanguageColor(language) {
      if (!language) return "grey";
      return this.languageColors[language] || "grey-darken-1";
    },

    truncateReadme(content) {
      if (!content) return "";

      // Maximum 500 characters
      const maxLength = 500;
      if (content.length <= maxLength) return content;

      return content.substring(0, maxLength) + "...";
    },
  },
  created() {
    // Initialize username input from store
    this.usernameInput = this.username;

    // Load projects
    this.getProjects();

    // Check rate limit
    this.checkRateLimit();
  },
};
</script>

<style scoped>
.h-100 {
  height: 100%;
}
.flex-grow-1 {
  flex-grow: 1;
}
.readme-content {
  white-space: pre-line;
  font-family: monospace;
  font-size: 0.85rem;
  max-height: 300px;
  overflow-y: auto;
  background-color: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
}
</style>
