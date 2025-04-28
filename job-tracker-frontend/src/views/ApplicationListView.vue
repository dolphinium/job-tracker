<template>
  <main-layout>
    <!-- Use flat or low elevation for card -->
    <v-card flat class="pa-0">
      <v-card-title class="d-flex align-center pa-4">
        <span class="text-h6 font-weight-regular">Applications</span>
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-inner-icon="mdi-magnify"
          label="Search Applications"
          single-line
          hide-details
          density="compact"
          variant="outlined"
          class="mr-4"
          style="max-width: 300px"
        ></v-text-field>
        <v-btn
          color="primary"
          to="/applications/new"
          prepend-icon="mdi-plus"
          variant="flat"
        >
          <!-- Flat variant -->
          New Application
        </v-btn>
      </v-card-title>

      <v-divider></v-divider>

      <!-- Add hover effect, density -->
      <v-data-table
        :headers="headers"
        :items="applications"
        :search="search"
        :loading="loading"
        class="pa-0"
        item-value="id"
        :items-per-page="15"
        hover
        density="comfortable"
      >
        <!-- Column Templates using v-slot:[`item.key`] -->
        <template v-slot:[`item.company`]="{ item }">
          <div class="font-weight-medium">{{ item.company || "-" }}</div>
        </template>

        <template v-slot:[`item.status`]="{ item }">
          <!-- Use tonal variant for softer chips -->
          <v-chip
            :color="getStatusColor(item.status)"
            size="small"
            variant="tonal"
            label
          >
            {{ item.status }}
          </v-chip>
        </template>

        <template v-slot:[`item.date_posted`]="{ item }">
          <span class="text-grey-darken-1">{{
            formatDate(item.date_posted)
          }}</span>
        </template>

        <template v-slot:[`item.applied_date`]="{ item }">
          <span class="text-grey-darken-1">{{
            formatDate(item.applied_date)
          }}</span>
        </template>

        <template v-slot:[`item.linkedin_url`]="{ item }">
          <v-tooltip location="top" text="Open LinkedIn Page">
            <template v-slot:activator="{ props }">
              <v-btn
                v-if="item.linkedin_url"
                icon
                variant="text"
                color="blue-darken-1"
                :href="item.linkedin_url"
                target="_blank"
                rel="noopener noreferrer"
                size="small"
                v-bind="props"
              >
                <v-icon size="medium">mdi-linkedin</v-icon>
              </v-btn>
            </template>
          </v-tooltip>
        </template>

        <template v-slot:[`item.actions`]="{ item }">
          <v-tooltip location="top" text="Edit Application">
            <template v-slot:activator="{ props }">
              <v-btn
                icon
                variant="text"
                size="small"
                color="grey-darken-1"
                :to="`/applications/${item.id}`"
                v-bind="props"
              >
                <v-icon size="medium">mdi-pencil-outline</v-icon>
                <!-- Outline icon -->
              </v-btn>
            </template>
          </v-tooltip>
          <v-tooltip location="top" text="Delete Application">
            <template v-slot:activator="{ props }">
              <v-btn
                icon
                variant="text"
                size="small"
                color="grey-darken-1"
                @click="confirmDelete(item)"
                v-bind="props"
              >
                <v-icon size="medium">mdi-delete-outline</v-icon>
                <!-- Outline icon -->
              </v-btn>
            </template>
          </v-tooltip>
        </template>

        <template v-slot:loading>
          <v-skeleton-loader type="table-tbody"></v-skeleton-loader>
          <!-- Cleaner loading -->
        </template>

        <template v-slot:no-data>
          <div class="text-center pa-4">
            <v-icon size="large" color="grey-lighten-1" class="mb-2"
              >mdi-text-box-search-outline</v-icon
            >
            <div class="text-grey">No applications found.</div>
            <v-btn
              color="primary"
              class="mt-4"
              size="small"
              to="/applications/new"
              variant="flat"
            >
              Create Your First Application
            </v-btn>
          </div>
        </template>
      </v-data-table>

      <!-- Delete Confirmation Dialog - Refined Design -->
      <v-dialog v-model="deleteDialog" max-width="450px" persistent>
        <!-- Persistent -->
        <v-card rounded="lg">
          <!-- Rounded corners -->
          <v-card-title
            class="text-h6 font-weight-regular pa-4 d-flex justify-space-between align-center"
          >
            <span>Confirm Deletion</span>
            <v-btn
              icon
              variant="text"
              @click="deleteDialog = false"
              size="small"
              ><v-icon>mdi-close</v-icon></v-btn
            >
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text class="pa-4 text-body-1">
            Are you sure you want to permanently delete the application for
            <strong class="font-weight-medium">{{
              applicationToDelete?.title || "this job"
            }}</strong>
            at
            <strong class="font-weight-medium">{{
              applicationToDelete?.company || "this company"
            }}</strong
            >? <br /><br />
            <span class="text-grey-darken-1"
              >This action cannot be undone.</span
            >
          </v-card-text>
          <v-divider></v-divider>
          <v-card-actions class="pa-4">
            <v-spacer></v-spacer>
            <v-btn
              color="grey-darken-1"
              variant="text"
              @click="deleteDialog = false"
              >Cancel</v-btn
            >
            <v-btn color="error" variant="flat" @click="handleDeleteConfirm"
              >Delete Application</v-btn
            >
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-card>
  </main-layout>
</template>

<script>
// ... (script remains largely the same, ensure computed/methods are correct as per previous step)
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
        // Key names match data properties
        {
          title: "Company",
          key: "company",
          align: "start",
          sortable: true,
          minWidth: "150px",
        },
        {
          title: "Position",
          key: "title",
          align: "start",
          sortable: true,
          minWidth: "200px",
        },
        {
          title: "Location",
          key: "location",
          align: "start",
          sortable: true,
          minWidth: "150px",
        },
        {
          title: "Posted",
          key: "date_posted",
          align: "start",
          sortable: true,
          minWidth: "120px",
        },
        {
          title: "Applied",
          key: "applied_date",
          align: "start",
          sortable: true,
          minWidth: "120px",
        },
        {
          title: "Status",
          key: "status",
          align: "center",
          sortable: true,
          minWidth: "120px",
        },
        {
          title: "LinkedIn",
          key: "linkedin_url",
          align: "center",
          sortable: false,
        },
        {
          title: "Actions",
          key: "actions",
          align: "end",
          sortable: false,
          minWidth: "100px",
        }, // Align actions end
      ],
    };
  },
  computed: {
    ...mapState("applications", ["applications", "loading", "error"]),
  },
  methods: {
    ...mapActions("applications", ["fetchApplications", "deleteApplication"]),
    formatDate(dateString) {
      if (!dateString) return "–"; // Use em dash for empty
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return "Invalid";
        // More concise format
        return date.toLocaleDateString(undefined, {
          year: "numeric",
          month: "short",
          day: "numeric",
        });
      } catch (e) {
        return "Invalid";
      }
    },
    getStatusColor(status) {
      // Using semantic colors where appropriate
      const colors = {
        Wishlist: "grey",
        Applied: "blue",
        Screening: "orange",
        Interview: "purple",
        "Technical Test": "deep-purple",
        "Final Interview": "cyan darken-1",
        Offer: "teal",
        Accepted: "success",
        Rejected: "error",
        Withdrawn: "blue-grey",
      };
      return colors[status] || "grey";
    },
    confirmDelete(item) {
      this.applicationToDelete = item;
      this.deleteDialog = true;
    },
    async handleDeleteConfirm() {
      // ... (delete logic remains the same)
      if (this.applicationToDelete && this.applicationToDelete.id) {
        try {
          await this.deleteApplication(this.applicationToDelete.id);
          this.deleteDialog = false;
          this.applicationToDelete = null;
        } catch (error) {
          console.error("Failed to delete application:", error);
          // TODO: Show user feedback (snackbar)
          this.deleteDialog = false;
          this.applicationToDelete = null;
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
/* Target header text for slight boldness */
:deep(.v-data-table-header__content span) {
  font-weight: 500;
  color: #424242; /* Darker grey */
}
/* Ensure enough space for end-aligned actions */
:deep(td:last-child) {
  text-align: right;
}
</style>
