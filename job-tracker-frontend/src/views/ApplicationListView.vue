<template>
  <main-layout>
    <v-card>
      <v-card-title>
        Applications
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-inner-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
          density="compact"
        ></v-text-field>
        <v-spacer></v-spacer>
        <v-btn color="primary" to="/applications/new" prepend-icon="mdi-plus">
          <!-- Use prepend-icon -->
          New Application
        </v-btn>
      </v-card-title>

      <!-- Use v-data-table -->
      <v-data-table
        :headers="headers"
        :items="applications"
        :search="search"
        :loading="loading"
        class="elevation-1"
        item-value="id"
        :items-per-page="10"
      >
        <!-- Column Templates using v-slot:[`item.key`] -->
        <template v-slot:[`item.status`]="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            text-color="white"
            size="small"
          >
            {{ item.status }}
          </v-chip>
        </template>

        <template v-slot:[`item.date_posted`]="{ item }">
          {{ formatDate(item.date_posted) }}
        </template>

        <template v-slot:[`item.applied_date`]="{ item }">
          {{ formatDate(item.applied_date) }}
        </template>

        <template v-slot:[`item.linkedin_url`]="{ item }">
          <v-btn
            v-if="item.linkedin_url"
            icon
            variant="text"
            color="blue-darken-1"
            :href="item.linkedin_url"
            target="_blank"
            rel="noopener noreferrer"
            size="small"
            title="Open LinkedIn Page"
          >
            <v-icon>mdi-linkedin</v-icon>
          </v-btn>
        </template>

        <template v-slot:[`item.actions`]="{ item }">
          <v-btn
            icon
            variant="text"
            size="small"
            color="primary"
            :to="`/applications/${item.id}`"
            title="Edit Application"
          >
            <v-icon>mdi-pencil</v-icon>
            <!-- Edit icon -->
          </v-btn>
          <v-btn
            icon
            variant="text"
            size="small"
            color="error"
            @click="confirmDelete(item)"
            title="Delete Application"
          >
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>

        <!-- Optional: Loading state -->
        <template v-slot:loading>
          <v-skeleton-loader type="table-row@10"></v-skeleton-loader>
        </template>

        <!-- Optional: No data state -->
        <template v-slot:no-data>
          No applications found.
          <v-btn
            color="primary"
            class="ml-2"
            size="small"
            to="/applications/new"
            >Create One</v-btn
          >
        </template>
      </v-data-table>

      <!-- Delete Confirmation Dialog -->
      <v-dialog v-model="deleteDialog" max-width="500px">
        <v-card>
          <v-card-title class="text-h5">Delete Application?</v-card-title>
          <v-card-text>
            Are you sure you want to delete the application for
            <strong>{{ applicationToDelete?.title || "this job" }}</strong>
            at
            <strong>{{ applicationToDelete?.company || "this company" }}</strong
            >? This action cannot be undone.
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey" variant="text" @click="deleteDialog = false"
              >Cancel</v-btn
            >
            <v-btn color="error" variant="flat" @click="handleDeleteConfirm"
              >Confirm Delete</v-btn
            >
            <v-spacer></v-spacer>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-card>
  </main-layout>
</template>

<script>
import { mapState, mapActions } from "vuex";
import MainLayout from "@/layouts/MainLayout.vue";

export default {
  name: "ApplicationListView",
  components: {
    MainLayout,
  },
  data() {
    return {
      search: "",
      deleteDialog: false,
      applicationToDelete: null, // Store the whole item for context in dialog
      // Updated headers for Vuetify 3 v-data-table
      headers: [
        { title: "Company", key: "company", align: "start", sortable: true },
        { title: "Position", key: "title", align: "start", sortable: true },
        { title: "Location", key: "location", align: "start", sortable: true },
        {
          title: "Job Post Date",
          key: "date_posted",
          align: "start",
          sortable: true,
        },
        {
          title: "Applied Date",
          key: "applied_date",
          align: "start",
          sortable: true,
        },
        { title: "Status", key: "status", align: "center", sortable: true },
        {
          title: "LinkedIn",
          key: "linkedin_url",
          align: "center",
          sortable: false,
        },
        { title: "Actions", key: "actions", align: "center", sortable: false },
      ],
    };
  },
  computed: {
    // Make sure error state is mapped if you want to display errors
    ...mapState("applications", ["applications", "loading", "error"]),
  },
  methods: {
    ...mapActions("applications", ["fetchApplications", "deleteApplication"]),
    formatDate(dateString) {
      if (!dateString) return "N/A";
      try {
        const date = new Date(dateString);
        // Check if the date is valid
        if (isNaN(date.getTime())) return "Invalid Date";
        return date.toLocaleDateString(); // Adjust options as needed e.g., { year: 'numeric', month: 'short', day: 'numeric' }
      } catch (e) {
        return "Invalid Date";
      }
    },
    getStatusColor(status) {
      const colors = {
        Wishlist: "grey",
        Applied: "blue",
        Screening: "orange",
        Interview: "purple",
        "Technical Test": "deep-purple accent-4", // Example alternative
        "Final Interview": "cyan", // Example alternative
        Offer: "teal",
        Accepted: "success", // Use Vuetify semantic colors
        Rejected: "error", // Use Vuetify semantic colors
        Withdrawn: "blue-grey", // Example alternative
      };
      return colors[status] || "grey"; // Default color
    },
    confirmDelete(item) {
      this.applicationToDelete = item; // Store the whole item
      this.deleteDialog = true;
    },
    async handleDeleteConfirm() {
      if (this.applicationToDelete && this.applicationToDelete.id) {
        try {
          await this.deleteApplication(this.applicationToDelete.id); // Pass only the ID
          // Optionally show success message
          this.deleteDialog = false;
          this.applicationToDelete = null; // Clear stored item
        } catch (error) {
          console.error("Failed to delete application:", error);
          // Optionally show error message from this.error
          this.deleteDialog = false; // Close dialog even on error
          this.applicationToDelete = null; // Clear item anyway
        }
      }
    },
  },
  created() {
    this.fetchApplications();
  },
};
</script>

<style scoped>
/* Optional: Add custom styles if needed */
.v-data-table {
  margin-top: 16px;
}
</style>
