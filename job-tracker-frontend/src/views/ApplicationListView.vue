<template>
  <main-layout>
    <v-card>
      <v-card-title>
        Applications
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
        ></v-text-field>
        <v-spacer></v-spacer>
        <v-btn color="primary" to="/applications/new">
          <v-icon left>mdi-plus</v-icon>
          New Application
        </v-btn>
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="applications"
        :search="search"
        :loading="loading"
        class="elevation-1"
      >
        <template v-slot:[`item.status`]="{ item }">
          <v-chip :color="getStatusColor(item.status)" text-color="white" small>
            {{ item.status }}
          </v-chip>
        </template>
        <template v-slot:[`item.applied_date`]="{ item }">
          {{ formatDate(item.applied_date) }}
        </template>
        <template v-slot:[`item.actions`]="{ item }">
          <v-btn icon small color="primary" :to="`/applications/${item.id}`">
            <v-icon>mdi-eye</v-icon>
          </v-btn>
          <v-btn icon small color="error" @click="confirmDelete(item)">
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>

      <v-dialog v-model="deleteDialog" max-width="500px">
        <v-card>
          <v-card-title>Delete Application</v-card-title>
          <v-card-text>
            Are you sure you want to delete this application?
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="error" text @click="deleteDialog = false"
              >Cancel</v-btn
            >
            <v-btn color="primary" text @click="handleDeleteConfirm"
              >Confirm</v-btn
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
      applicationToDelete: null,
      headers: [
        { text: "Company", value: "company" },
        { text: "Position", value: "title" },
        { text: "Location", value: "location" },
        { text: "Status", value: "status" },
        { text: "Applied Date", value: "applied_date" },
        { text: "Actions", value: "actions", sortable: false },
      ],
    };
  },
  computed: {
    ...mapState("applications", ["applications", "loading"]),
  },
  methods: {
    ...mapActions("applications", ["fetchApplications", "deleteApplication"]),
    formatDate(dateString) {
      if (!dateString) return "N/A";
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    getStatusColor(status) {
      const colors = {
        Wishlist: "grey",
        Applied: "blue",
        Screening: "orange",
        Interview: "purple",
        "Technical Test": "red",
        "Final Interview": "green",
        Offer: "teal",
        Accepted: "green darken-2",
        Rejected: "red darken-2",
        Withdrawn: "grey darken-1",
      };
      return colors[status] || "grey";
    },
    confirmDelete(item) {
      this.applicationToDelete = item.id;
      this.deleteDialog = true;
    },
    async handleDeleteConfirm() {
      if (this.applicationToDelete) {
        try {
          // Call the mapped Vuex action 'deleteApplication'
          // Pass the stored ID as the payload
          await this.deleteApplication(this.applicationToDelete);

          // Close the dialog and clear the ID only after success
          this.deleteDialog = false;
          this.applicationToDelete = null;
        } catch (error) {
          console.error("Failed to delete application:", error);
          // Optionally: Show an error message to the user (e.g., using a snackbar)
          this.deleteDialog = false; // Close dialog even on error
          this.applicationToDelete = null; // Clear ID anyway
        }
      }
    },
  },
  created() {
    this.fetchApplications();
  },
};
</script>
