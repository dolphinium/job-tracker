<template>
  <div>
    <v-card flat class="mb-4">
      <v-card-title class="d-flex align-center">
        <span class="text-h6 font-weight-regular">Generate HR Email</span>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          variant="flat"
          size="small"
          prepend-icon="mdi-email-outline"
          :loading="emailGenerationLoading"
          :disabled="selectedProjects.length === 0 || emailGenerationLoading"
          @click="handleGenerateEmail"
        >
          Generate Email
        </v-btn>
      </v-card-title>

      <v-divider></v-divider>

      <v-card-text>
        <p class="text-body-1 mb-4">
          Select relevant GitHub projects to include in your personalized email
          to HR.
        </p>

        <v-alert
          v-if="emailGenerationError"
          type="error"
          variant="tonal"
          class="mb-4"
          closable
          @click:close="emailGenerationError = null"
        >
          {{ emailGenerationError }}
        </v-alert>

        <v-row>
          <v-col cols="12" md="8">
            <v-card variant="outlined" class="mb-4">
              <v-card-title class="text-subtitle-1">
                Select Relevant Projects
              </v-card-title>
              <v-divider></v-divider>
              <v-card-text class="pa-0">
                <v-list select-strategy="multiple" v-model="selectedProjects">
                  <v-list-item
                    v-for="project in projects"
                    :key="project.id"
                    :value="project.id"
                    :title="project.name"
                    :subtitle="project.description || 'No description'"
                  >
                    <template v-slot:prepend>
                      <v-checkbox-btn
                        v-model="selectedProjects"
                        :value="project.id"
                      ></v-checkbox-btn>
                    </template>
                    <template v-slot:append>
                      <v-chip
                        v-if="project.language"
                        size="small"
                        color="primary"
                        variant="flat"
                        class="mr-2"
                      >
                        {{ project.language }}
                      </v-chip>
                    </template>
                  </v-list-item>

                  <v-list-item v-if="projects.length === 0">
                    <div class="text-center pa-4 w-100">
                      <v-icon size="large" color="grey-lighten-1" class="mb-2">
                        mdi-github
                      </v-icon>
                      <div class="text-body-1 text-grey-darken-1">
                        No GitHub projects found. Import your projects from the
                        <router-link to="/github">GitHub Projects</router-link>
                        page.
                      </div>
                    </div>
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card variant="outlined" class="mb-4">
              <v-card-title class="text-subtitle-1">
                Email Options
              </v-card-title>
              <v-divider></v-divider>
              <v-card-text>
                <v-radio-group v-model="language" class="mt-2">
                  <v-radio value="english" label="English"></v-radio>
                  <v-radio value="turkish" label="Turkish"></v-radio>
                </v-radio-group>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Generated Email Display -->
    <v-card v-if="generatedEmail" flat class="mb-4">
      <v-card-title class="d-flex align-center">
        <span class="text-h6 font-weight-regular">Generated Email</span>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          variant="text"
          size="small"
          prepend-icon="mdi-content-copy"
          @click="copyEmailToClipboard"
        >
          Copy to Clipboard
        </v-btn>
      </v-card-title>

      <v-divider></v-divider>

      <v-card-text>
        <v-alert
          v-if="copySuccess"
          type="success"
          variant="tonal"
          class="mb-4"
          closable
          @click:close="copySuccess = false"
        >
          Email copied to clipboard!
        </v-alert>

        <v-sheet
          class="pa-4 bg-grey-lighten-4 rounded"
          style="white-space: pre-wrap; font-family: 'Roboto', sans-serif"
        >
          {{ generatedEmail }}
        </v-sheet>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from "vuex";

export default {
  name: "EmailGenerator",
  props: {
    applicationId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      selectedProjects: [],
      language: "english",
      copySuccess: false,
    };
  },
  computed: {
    ...mapState("github", ["projects"]),
    ...mapGetters("applications", [
      "generatedEmail",
      "emailGenerationLoading",
      "emailGenerationError",
    ]),
  },
  methods: {
    ...mapActions("github", ["getProjects"]),
    ...mapActions("applications", ["generateEmail"]),

    async handleGenerateEmail() {
      if (this.selectedProjects.length === 0) {
        return;
      }

      try {
        await this.generateEmail({
          applicationId: this.applicationId,
          projectIds: this.selectedProjects,
          language: this.language,
        });

        // Scroll to the generated email
        this.$nextTick(() => {
          const emailElement = document.querySelector(".generated-email");
          if (emailElement) {
            emailElement.scrollIntoView({ behavior: "smooth" });
          }
        });
      } catch (error) {
        console.error("Failed to generate email:", error);
      }
    },

    copyEmailToClipboard() {
      if (!this.generatedEmail) return;

      navigator.clipboard
        .writeText(this.generatedEmail)
        .then(() => {
          this.copySuccess = true;
          setTimeout(() => {
            this.copySuccess = false;
          }, 3000);
        })
        .catch((err) => {
          console.error("Failed to copy email: ", err);
        });
    },
  },
  created() {
    // Load GitHub projects if not already loaded
    this.getProjects();
  },
};
</script>

<style scoped>
.v-list-item {
  min-height: 64px;
}
</style>
