// job-tracker-frontend/src/views/ApplicationFormView.vue
<template>
  <main-layout>
    <v-card>
      <v-card-title>
        {{ isEdit ? "Edit Application" : "New Application" }}
      </v-card-title>
      <v-card-text>
        <!-- Added validation checking for the form -->
        <v-form ref="formRef" v-model="valid" @submit.prevent="saveApplication">
          <v-text-field
            v-model="form.linkedin_url"
            label="LinkedIn Job URL"
            required
            :rules="[(v) => !!v || 'URL is required']"
          ></v-text-field>

          <v-text-field v-model="form.title" label="Job Title"></v-text-field>

          <v-text-field v-model="form.company" label="Company"></v-text-field>

          <v-text-field v-model="form.location" label="Location"></v-text-field>

          <v-select
            v-model="form.status"
            :items="statusOptions"
            label="Status"
            required
          ></v-select>

          <!-- Updated v-menu activator for Vuetify 3 -->
          <!-- And v-date-picker model handling -->
          <v-menu
            v-model="dateMenu"
            :close-on-content-click="false"
            min-width="auto"
          >
            <template v-slot:activator="{ props }">
              <v-text-field
                :model-value="formattedDate"
                label="Applied Date"
                readonly
                v-bind="props"
                clearable
                @click:clear="form.applied_date = null"
              ></v-text-field>
            </template>
            <v-date-picker
              v-model="form.applied_date"
              @update:modelValue="dateMenu = false"
              title="Applied Date"
              show-adjacent-months
            ></v-date-picker>
          </v-menu>

          <v-textarea
            v-model="form.job_description"
            label="Job Description"
            rows="5"
          ></v-textarea>

          <v-textarea v-model="form.notes" label="Notes" rows="3"></v-textarea>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="grey" variant="text" :to="'/applications'">
          Cancel
        </v-btn>
        <!-- Updated styling -->
        <v-btn
          color="primary"
          :loading="loading"
          :disabled="!valid"
          @click="saveApplication"
        >
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </main-layout>
</template>

<script>
import { mapState, mapActions } from "vuex";
import MainLayout from "@/layouts/MainLayout.vue";

export default {
  name: "ApplicationFormView",
  components: {
    MainLayout,
  },
  data() {
    return {
      valid: false, // Will be updated by the form
      formRef: null, // To reference the v-form
      form: {
        linkedin_url: "",
        title: "",
        company: "",
        location: "",
        job_description: "",
        applied_date: null, // Initialize as null
        status: "Wishlist",
        notes: "",
        // Add fields that exist in the backend model but might not be directly edited here,
        // to avoid sending undefined if they were loaded
        date_posted: null,
        linkedin_job_id: null,
        status_history: [],
        documents: [],
        contacts: [],
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
    ...mapState("applications", ["loading", "currentApplication", "error"]), // Added error state
    isEdit() {
      return !!this.$route.params.id;
    },
    formattedDate() {
      // Handle both Date objects and date strings (YYYY-MM-DD) from picker
      if (!this.form.applied_date) return "";
      try {
        // Attempt to parse the date string/object robustly
        const date = new Date(this.form.applied_date);
        // Check if the date is valid after parsing
        if (isNaN(date.getTime())) {
          // If it's not a valid date (e.g., just "YYYY-MM-DD"), create date considering local timezone offset
          // This handles the case where the date picker returns a string like "2023-10-27"
          const parts = this.form.applied_date.split("-");
          if (parts.length === 3) {
            const adjustedDate = new Date(parts[0], parts[1] - 1, parts[2]);
            return adjustedDate.toLocaleDateString();
          }
          return ""; // Invalid date format
        }
        return date.toLocaleDateString();
      } catch (e) {
        console.error("Error formatting date:", e);
        return ""; // Return empty string on error
      }
    },
  },
  methods: {
    ...mapActions("applications", [
      "createApplication",
      "updateApplication",
      "fetchApplication",
    ]),
    async saveApplication() {
      // Access validate function via the ref
      const { valid } = await this.$refs.formRef.validate();
      if (valid) {
        try {
          // Ensure applied_date is null if empty, or correct format otherwise
          const payload = { ...this.form };
          if (payload.applied_date instanceof Date) {
            // Optionally format to ISO string if backend expects full datetime
            // payload.applied_date = payload.applied_date.toISOString();
            // Or let Pydantic handle the conversion from Date object if backend accepts it
          } else if (!payload.applied_date) {
            payload.applied_date = null; // Ensure it's null, not empty string
          }
          // Remove fields that shouldn't be sent on update/create if they were just placeholders
          delete payload.status_history;
          delete payload.documents;
          delete payload.contacts;

          if (this.isEdit) {
            await this.updateApplication({
              id: this.$route.params.id,
              // Send only fields present in ApplicationUpdate model
              data: {
                title: payload.title,
                company: payload.company,
                location: payload.location,
                job_description: payload.job_description,
                date_posted: payload.date_posted, // Keep original if not editable
                applied_date: payload.applied_date,
                status: payload.status,
                notes: payload.notes,
              },
            });
          } else {
            await this.createApplication(payload);
          }
          this.$router.push("/applications");
        } catch (error) {
          console.error("Error saving application:", error);
          // Optionally show error to user using a snackbar or alert
          // e.g., this.showSnackbar(this.error || 'Failed to save application');
        }
      } else {
        console.log("Form is not valid");
      }
    },
    // Helper to format date strings from backend (ISO format) to YYYY-MM-DD for picker if needed
    formatDateForPicker(dateString) {
      if (!dateString) return null;
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return null; // Invalid date
        // Return in YYYY-MM-DD format which v-date-picker handles well
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, "0");
        const day = date.getDate().toString().padStart(2, "0");
        return `${year}-${month}-${day}`;
      } catch (e) {
        return null;
      }
    },
  },
  async created() {
    if (this.isEdit) {
      await this.fetchApplication(this.$route.params.id);
      if (this.currentApplication) {
        // Copy values to form more carefully
        Object.keys(this.form).forEach((key) => {
          if (
            this.currentApplication[key] !== undefined &&
            this.currentApplication[key] !== null
          ) {
            // Specifically handle date formatting for the date picker if necessary
            if (key === "applied_date") {
              // v-date-picker v-model should handle the date object or ISO string
              // If it comes as ISO string, directly assign it. If you need Date object:
              // this.form[key] = new Date(this.currentApplication[key]);
              // Assign directly, v-date-picker model should handle it
              this.form[key] = this.currentApplication[key];
            } else {
              this.form[key] = this.currentApplication[key];
            }
          }
        });
        // Ensure applied_date is null if it wasn't set in the loaded data
        if (!this.form.applied_date) {
          this.form.applied_date = null;
        }
      } else if (this.error) {
        console.error("Error fetching application:", this.error);
        // Redirect or show error message
      }
    }
  },
  mounted() {
    // Assign the ref after component is mounted
    this.formRef = this.$refs.formRef;
  },
};
</script>
