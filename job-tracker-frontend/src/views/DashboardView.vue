<template>
  <main-layout>
    <v-row>
      <!-- Summary Cards -->
      <v-col cols="12" md="4">
        <v-card outlined class="fill-height">
          <v-card-title>Total Applications</v-card-title>
          <v-card-text class="text-h4 text-center pa-5">
            <v-progress-circular
              v-if="loading"
              indeterminate
              color="primary"
            ></v-progress-circular>
            <span v-else>{{ applications.length }}</span>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card outlined class="fill-height">
          <v-card-title>Active Applications</v-card-title>
          <v-card-text class="text-h4 text-center pa-5">
            <v-progress-circular
              v-if="loading"
              indeterminate
              color="info"
            ></v-progress-circular>
            <span v-else>{{ activeApplications.length }}</span>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card outlined class="fill-height">
          <v-card-title>Interview Stage</v-card-title>
          <v-card-text class="text-h4 text-center pa-5">
            <v-progress-circular
              v-if="loading"
              indeterminate
              color="success"
            ></v-progress-circular>
            <span v-else>{{ interviewApplications.length }}</span>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Recent Applications Table -->
      <v-col cols="12">
        <v-card class="mt-4">
          <v-card-title>
            Recent Applications
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              size="small"
              to="/applications/new"
              prepend-icon="mdi-plus"
            >
              New Application
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="recentApplications"
              :loading="loading"
              :items-per-page="5"
              class="elevation-1"
              item-value="id"
            >
              <!-- Column Templates copied from ApplicationListView -->
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
                </v-btn>
                <!-- No delete button on dashboard recent view, keep it cleaner -->
              </template>

              <!-- Optional: Loading state -->
              <template v-slot:loading>
                <v-skeleton-loader type="table-row@5"></v-skeleton-loader>
              </template>

              <!-- Optional: No data state -->
              <template v-slot:no-data>
                <span v-if="loading">Loading recent applications...</span>
                <span v-else>No recent applications to display.</span>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </main-layout>
</template>

<script>
import { mapState, mapActions } from "vuex";
import MainLayout from "@/layouts/MainLayout.vue";

export default {
  name: "DashboardView",
  components: {
    MainLayout,
  },
  data() {
    return {
      // Headers copied from ApplicationListView (actions might differ slightly)
      headers: [
        { title: "Company", key: "company", align: "start", sortable: true },
        { title: "Position", key: "title", align: "start", sortable: true },
        { title: "Location", key: "location", align: "start", sortable: false }, // Less sort relevance here
        {
          title: "Job Post Date",
          key: "date_posted",
          align: "start",
          sortable: false,
        },
        {
          title: "Applied Date",
          key: "applied_date",
          align: "start",
          sortable: true,
        }, // Sort by applied might be useful
        { title: "Status", key: "status", align: "center", sortable: false },
        {
          title: "LinkedIn",
          key: "linkedin_url",
          align: "center",
          sortable: false,
        },
        { title: "Actions", key: "actions", align: "center", sortable: false }, // Keep Actions, just show edit
      ],
    };
  },
  computed: {
    ...mapState("applications", ["applications", "loading"]),
    recentApplications() {
      // Sort by created_at for "recent"
      return [...this.applications]
        .sort((a, b) => {
          // Handle potentially null dates
          const dateA = a.created_at ? new Date(a.created_at) : 0;
          const dateB = b.created_at ? new Date(b.created_at) : 0;
          return dateB - dateA; // Descending order
        })
        .slice(0, 5); // Show top 5
    },
    activeApplications() {
      const activeStatuses = [
        "Wishlist",
        "Applied",
        "Screening",
        "Interview",
        "Technical Test",
        "Final Interview",
        "Offer",
      ];
      return this.applications.filter((app) =>
        activeStatuses.includes(app.status)
      );
    },
    interviewApplications() {
      const interviewStatuses = [
        "Interview",
        "Technical Test",
        "Final Interview",
      ];
      return this.applications.filter((app) =>
        interviewStatuses.includes(app.status)
      );
    },
  },
  methods: {
    ...mapActions("applications", ["fetchApplications"]),
    // Copied from ApplicationListView
    formatDate(dateString) {
      if (!dateString) return "N/A";
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return "Invalid Date";
        return date.toLocaleDateString();
      } catch (e) {
        return "Invalid Date";
      }
    },
    // Copied from ApplicationListView
    getStatusColor(status) {
      const colors = {
        Wishlist: "grey",
        Applied: "blue",
        Screening: "orange",
        Interview: "purple",
        "Technical Test": "deep-purple accent-4",
        "Final Interview": "cyan",
        Offer: "teal",
        Accepted: "success",
        Rejected: "error",
        Withdrawn: "blue-grey",
      };
      return colors[status] || "grey";
    },
  },
  created() {
    // Fetch applications if not already loaded or if stale
    // Simple check: fetch if empty
    if (this.applications.length === 0) {
      this.fetchApplications();
    }
  },
};
</script>

<style scoped>
.v-card {
  display: flex;
  flex-direction: column;
}
.v-card.fill-height {
  height: 100%;
}
.v-card-text.text-center {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-grow: 1; /* Allows text to take available space */
}
</style>
