<template>
  <main-layout>
    <v-card max-width="800" class="mx-auto" flat v-if="!isEdit || loading">
      <!-- Flat card, optional max-width -->
      <v-card-title class="pa-4">
        <span class="text-h6 font-weight-regular">{{
          isEdit ? "Edit Application" : "New Application"
        }}</span>
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text class="pa-4 pa-md-6">
        <!-- Added spacing between fields using mb-4 -->
        <v-form
          ref="formRef"
          v-model="valid"
          @submit.prevent="saveApplication"
          lazy-validation
        >
          <v-text-field
            v-model="form.linkedin_url"
            label="LinkedIn Job URL"
            required
            :rules="urlRules"
            variant="outlined"
            density="compact"
            class="mb-4"
            prepend-inner-icon="mdi-linkedin"
          ></v-text-field>

          <v-row>
            <v-col cols="12" md="8">
              <v-text-field
                v-model="form.title"
                label="Job Title"
                variant="outlined"
                density="compact"
                class="mb-4"
                prepend-inner-icon="mdi-briefcase-outline"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="4">
              <v-select
                v-model="form.status"
                :items="statusOptions"
                label="Status"
                required
                variant="outlined"
                density="compact"
                class="mb-4"
                prepend-inner-icon="mdi-list-status"
              ></v-select>
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="form.company"
                label="Company"
                variant="outlined"
                density="compact"
                class="mb-4"
                prepend-inner-icon="mdi-domain"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="form.location"
                label="Location"
                variant="outlined"
                density="compact"
                class="mb-4"
                prepend-inner-icon="mdi-map-marker-outline"
              ></v-text-field>
            </v-col>
          </v-row>

          <v-menu
            v-model="dateMenu"
            :close-on-content-click="false"
            min-width="auto"
          >
            <template v-slot:activator="{ props }">
              <v-text-field
                :model-value="formattedDate"
                label="Applied Date (Optional)"
                readonly
                v-bind="props"
                variant="outlined"
                density="compact"
                class="mb-4"
                clearable
                @click:clear="form.applied_date = null"
                prepend-inner-icon="mdi-calendar-check-outline"
              ></v-text-field>
            </template>
            <v-date-picker
              v-model="form.applied_date"
              @update:modelValue="dateMenu = false"
              title="Applied Date"
              show-adjacent-months
              color="primary"
            ></v-date-picker>
          </v-menu>

          <v-textarea
            v-model="form.job_description"
            label="Job Description (auto-filled from LinkedIn)"
            rows="6"
            variant="outlined"
            density="compact"
            class="mb-4"
            readonly
            bg-color="grey-lighten-4"
          ></v-textarea>

          <v-textarea
            v-model="form.notes"
            label="Your Notes"
            rows="4"
            variant="outlined"
            density="compact"
            class="mb-4"
            prepend-inner-icon="mdi-note-text-outline"
          ></v-textarea>
        </v-form>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-actions class="pa-4">
        <v-spacer></v-spacer>
        <v-btn color="grey-darken-1" variant="text" :to="'/applications'">
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          :loading="loading"
          :disabled="!valid || loading"
          @click="saveApplication"
          variant="flat"
        >
          {{ isEdit ? "Save Changes" : "Create Application" }}
        </v-btn>
      </v-card-actions>
    </v-card>
    <!-- Optional: Snackbar for feedback -->
    <v-snackbar v-model="showSnackbar" :color="snackbarColor" timeout="3000">
      {{ snackbarText }}
      <template v-slot:actions>
        <v-btn color="white" variant="text" @click="showSnackbar = false"
          >Close</v-btn
        >
      </template>
    </v-snackbar>

    <!-- Email Generator Component for Edit Mode -->
    <div v-if="isEdit && currentApplication && !loading">
      <v-card max-width="800" class="mx-auto mb-6" flat>
        <v-card-title class="pa-4">
          <span class="text-h6 font-weight-regular">Edit Application</span>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pa-4">
          <v-alert
            type="info"
            variant="tonal"
            class="mb-4"
            icon="mdi-information-outline"
          >
            To edit application details, click the "Edit Details" button below.
          </v-alert>

          <div class="d-flex flex-column flex-sm-row mb-4">
            <v-btn
              color="primary"
              variant="outlined"
              prepend-icon="mdi-pencil"
              class="mb-2 mb-sm-0 mr-sm-2"
              @click="showEditForm = true"
            >
              Edit Details
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn
              color="error"
              variant="text"
              prepend-icon="mdi-delete"
              @click="confirmDelete"
            >
              Delete Application
            </v-btn>
          </div>

          <v-divider class="my-4"></v-divider>

          <!-- Application Summary -->
          <div class="mb-4">
            <h3 class="text-h6 mb-2">{{ currentApplication.title }}</h3>
            <div class="d-flex flex-wrap align-center mb-2">
              <span class="text-subtitle-1 font-weight-medium mr-2">{{
                currentApplication.company
              }}</span>
              <span
                v-if="currentApplication.location"
                class="text-body-2 text-grey-darken-1"
              >
                <v-icon size="small" class="mr-1">mdi-map-marker</v-icon>
                {{ currentApplication.location }}
              </span>
              <v-spacer></v-spacer>
              <v-chip
                :color="getStatusColor(currentApplication.status)"
                size="small"
                variant="tonal"
                class="ml-2"
              >
                {{ currentApplication.status }}
              </v-chip>
            </div>

            <div v-if="currentApplication.linkedin_url" class="mb-2">
              <v-btn
                variant="text"
                color="blue-darken-1"
                size="small"
                :href="currentApplication.linkedin_url"
                target="_blank"
                rel="noopener noreferrer"
                prepend-icon="mdi-linkedin"
              >
                View on LinkedIn
              </v-btn>
            </div>
          </div>
        </v-card-text>
      </v-card>

      <!-- Email Generator Component -->
      <email-generator :application-id="$route.params.id"></email-generator>
    </div>

    <!-- Edit Form Dialog -->
    <v-dialog v-model="showEditForm" max-width="800" persistent>
      <v-card>
        <v-card-title class="pa-4">
          <span class="text-h6">Edit Application Details</span>
          <v-spacer></v-spacer>
          <v-btn icon @click="showEditForm = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pa-4 pa-md-6">
          <v-form
            ref="editFormRef"
            v-model="valid"
            @submit.prevent="saveApplication"
            lazy-validation
          >
            <v-row>
              <v-col cols="12" md="8">
                <v-text-field
                  v-model="form.title"
                  label="Job Title"
                  variant="outlined"
                  density="compact"
                  class="mb-4"
                  prepend-inner-icon="mdi-briefcase-outline"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="form.status"
                  :items="statusOptions"
                  label="Status"
                  required
                  variant="outlined"
                  density="compact"
                  class="mb-4"
                  prepend-inner-icon="mdi-list-status"
                ></v-select>
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="form.company"
                  label="Company"
                  variant="outlined"
                  density="compact"
                  class="mb-4"
                  prepend-inner-icon="mdi-domain"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="form.location"
                  label="Location"
                  variant="outlined"
                  density="compact"
                  class="mb-4"
                  prepend-inner-icon="mdi-map-marker-outline"
                ></v-text-field>
              </v-col>
            </v-row>

            <v-menu
              v-model="dateMenu"
              :close-on-content-click="false"
              min-width="auto"
            >
              <template v-slot:activator="{ props }">
                <v-text-field
                  :model-value="formattedDate"
                  label="Applied Date (Optional)"
                  readonly
                  v-bind="props"
                  variant="outlined"
                  density="compact"
                  class="mb-4"
                  clearable
                  @click:clear="form.applied_date = null"
                  prepend-inner-icon="mdi-calendar-check-outline"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="form.applied_date"
                @update:modelValue="dateMenu = false"
                title="Applied Date"
                show-adjacent-months
                color="primary"
              ></v-date-picker>
            </v-menu>

            <v-textarea
              v-model="form.notes"
              label="Your Notes"
              rows="4"
              variant="outlined"
              density="compact"
              class="mb-4"
              prepend-inner-icon="mdi-note-text-outline"
            ></v-textarea>
          </v-form>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn
            color="grey-darken-1"
            variant="text"
            @click="showEditForm = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            :loading="loading"
            :disabled="!valid || loading"
            @click="saveApplication"
            variant="flat"
          >
            Save Changes
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="450" persistent>
      <v-card>
        <v-card-title class="text-h6">Confirm Deletion</v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pa-4">
          Are you sure you want to delete this application for
          <strong>{{ currentApplication?.title }}</strong> at
          <strong>{{ currentApplication?.company }}</strong
          >?
          <p class="mt-2 text-grey-darken-1">This action cannot be undone.</p>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="grey-darken-1"
            variant="text"
            @click="showDeleteDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn color="error" variant="flat" @click="handleDeleteApplication">
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </main-layout>
</template>

<script>
// Import components and Vuex helpers
import { mapState, mapActions } from "vuex";
import MainLayout from "@/layouts/MainLayout.vue";
import EmailGenerator from "@/components/EmailGenerator.vue";

export default {
  name: "ApplicationFormView",
  components: {
    MainLayout,
    EmailGenerator,
  },
  data() {
    return {
      valid: false,
      formRef: null,
      showSnackbar: false,
      snackbarText: "",
      snackbarColor: "success",
      showEditForm: false,
      showDeleteDialog: false,
      urlRules: [
        (v) => !!v || "URL is required",
        (v) =>
          /^https?:\/\/.+/.test(v) || "URL must be valid (e.g., https://...)",
        // Optional stricter rule:
        // v => (v && (v.includes('linkedin.com/jobs/view/') || v.includes('linkedin.com/jobs/collections/'))) || 'Please provide a valid LinkedIn job URL (jobs/view/ or jobs/collections/)',
      ],
      form: {
        linkedin_url: "",
        title: "",
        company: "",
        location: "",
        job_description: "",
        applied_date: null,
        status: "Wishlist",
        notes: "",
        // Initialize other fields potentially loaded during edit
        date_posted: null,
        linkedin_job_id: null,
      },
      dateMenu: false,
      statusOptions: [
        "Wishlist",
        "Applied",
        "Screening",
        "Interview",
        "Technical Test",
        "Final Interview",
        "Offer",
        "Accepted",
        "Rejected",
        "Withdrawn",
      ],
    };
  },
  computed: {
    // 3. MAP Vuex state correctly
    ...mapState("applications", ["loading", "currentApplication", "error"]),

    isEdit() {
      return !!this.$route.params.id;
    },
    formattedDate() {
      // ... (keep the existing formattedDate logic)
      if (!this.form.applied_date) return "";
      try {
        const date = new Date(this.form.applied_date);
        if (isNaN(date.getTime())) {
          const parts = this.form.applied_date.split("-");
          if (parts.length === 3) {
            // Use UTC to avoid timezone shifts when creating from string parts
            const adjustedDate = new Date(
              Date.UTC(parts[0], parts[1] - 1, parts[2])
            );
            return adjustedDate.toLocaleDateString(undefined, {
              year: "numeric",
              month: "long",
              day: "numeric",
            });
          }
          return "";
        }
        return date.toLocaleDateString(undefined, {
          year: "numeric",
          month: "long",
          day: "numeric",
        });
      } catch (e) {
        console.error("Error formatting date:", e);
        return "";
      }
    },
  },
  methods: {
    // 4. MAP Vuex actions correctly
    ...mapActions("applications", [
      "createApplication",
      "updateApplication",
      "fetchApplication",
      "deleteApplication",
    ]),

    // Your custom methods
    showFeedback(message, isError = false) {
      this.snackbarText = message;
      this.snackbarColor = isError ? "error" : "success";
      this.showSnackbar = true;
    },
    getStatusColor(status) {
      // Using semantic colors where appropriate
      const colors = {
        Wishlist: "grey",
        Applied: "blue",
        Screening: "orange",
        Interview: "purple",
        "Technical Test": "deep-purple",
        "Final Interview": "cyan-darken-1",
        Offer: "teal",
        Accepted: "success",
        Rejected: "error",
        Withdrawn: "blue-grey",
      };
      return colors[status] || "grey";
    },

    confirmDelete() {
      this.showDeleteDialog = true;
    },

    async handleDeleteApplication() {
      try {
        await this.deleteApplication(this.$route.params.id);
        this.showFeedback("Application deleted successfully.");
        this.$router.push("/applications");
      } catch (error) {
        console.error("Error deleting application:", error);
        const detail =
          error?.response?.data?.detail ||
          this.error ||
          "Failed to delete application.";
        this.showFeedback(detail, true);
        this.showDeleteDialog = false;
      }
    },

    async saveApplication() {
      const formRef = this.showEditForm
        ? this.$refs.editFormRef
        : this.$refs.formRef;
      const { valid } = await formRef.validate();
      if (valid) {
        this.showFeedback("Saving...", false); // Optional: indicate saving starts
        try {
          const payload = { ...this.form };
          // Ensure applied_date is handled correctly (null or valid date)
          if (payload.applied_date instanceof Date) {
            // Backend might expect ISO string - convert if needed
            // payload.applied_date = payload.applied_date.toISOString();
            // Or keep as Date object if backend/Pydantic handles it
          } else if (!payload.applied_date || payload.applied_date === "") {
            payload.applied_date = null;
          } else {
            // If it's a string like YYYY-MM-DD, ensure it's handled correctly
            // Depending on backend, might need conversion or leave as string
          }

          // Remove fields not relevant for create/update payload if they exist in form state
          // delete payload.status_history; // Example if these were added to form state
          // delete payload.documents;
          // delete payload.contacts;

          if (this.isEdit) {
            // Ensure only fields allowed by ApplicationUpdate model are sent
            const updateData = {
              title: payload.title,
              company: payload.company,
              location: payload.location,
              // job_description: payload.job_description, // Usually not user-editable
              // date_posted: payload.date_posted, // Keep original unless editable
              applied_date: payload.applied_date,
              status: payload.status,
              notes: payload.notes,
            };
            await this.updateApplication({
              id: this.$route.params.id,
              data: updateData,
            }); // `this.updateApplication` is now available
            this.showFeedback("Application updated successfully.");
          } else {
            // `this.createApplication` is now available
            // Send fields relevant for ApplicationCreate
            const createData = {
              linkedin_url: payload.linkedin_url,
              title: payload.title,
              company: payload.company,
              location: payload.location,
              job_description: payload.job_description, // Include if backend uses it on create
              applied_date: payload.applied_date,
              status: payload.status,
              notes: payload.notes,
            };
            await this.createApplication(createData);
            this.showFeedback("Application created successfully.");
          }
          this.$router.push("/applications");
        } catch (error) {
          console.error("Error saving application:", error);
          // Use optional chaining for safer error access
          const detail =
            error?.response?.data?.detail ||
            this.error ||
            "Failed to save application.";
          this.showFeedback(detail, true);
        }
      } else {
        console.log("Form is not valid");
        this.showFeedback("Please fix the errors in the form.", true);
      }
    },
  },
  async created() {
    if (this.isEdit) {
      console.log(`Fetching application with ID: ${this.$route.params.id}`); // Debug log
      // `this.fetchApplication` is now available
      await this.fetchApplication(this.$route.params.id);
      if (this.currentApplication) {
        // Copy values to form, handling potential nulls/undefined
        Object.keys(this.form).forEach((key) => {
          if (this.currentApplication[key] !== undefined) {
            // Handle date specifically if needed, otherwise direct assign
            if (key === "applied_date" && this.currentApplication[key]) {
              // Ensure it's a format the date picker understands or convert
              // Often direct assignment works if it's ISO string or already Date
              this.form[key] = this.currentApplication[key];
            } else {
              this.form[key] = this.currentApplication[key];
            }
          }
        });
        // Ensure date is null if not present
        if (!this.form.applied_date) {
          this.form.applied_date = null;
        }
      } else if (this.error) {
        console.error("Error fetching application:", this.error);
        this.showFeedback(`Error loading application: ${this.error}`, true);
        // Optionally redirect back
        // this.$router.push("/applications");
      } else {
        console.warn(
          "Fetched application data is null or undefined, but no error reported."
        );
        this.showFeedback("Could not load application data.", true);
      }
    }
  },
  mounted() {
    this.formRef = this.$refs.formRef;
  },
};
</script>

<style scoped>
.v-card {
  border: 1px solid #e0e0e0; /* Subtle border instead of shadow */
}
.v-textarea[readonly] {
  cursor: default; /* Indicate non-editable */
}
</style>
