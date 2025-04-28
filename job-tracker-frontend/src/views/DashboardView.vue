<template>
  <main-layout>
    <v-row>
      <!-- Summary Cards -->
      <v-col cols="12" md="4">
        <v-card variant="outlined" class="fill-height pa-2">
          <!-- Outlined variant -->
          <v-card-item>
            <!-- Use v-card-item for structured content -->
            <template v-slot:prepend>
              <v-icon color="primary" size="x-large"
                >mdi-briefcase-variant-outline</v-icon
              >
            </template>
            <v-card-title class="text-subtitle-1 font-weight-medium"
              >Total Applications</v-card-title
            >
          </v-card-item>
          <v-card-text class="text-h4 text-center pb-4">
            <v-progress-circular
              v-if="loading"
              indeterminate
              color="primary"
              size="small"
            ></v-progress-circular>
            <span v-else>{{ applications.length }}</span>
          </v-card-text>
        </v-card>
      </v-col>
      <!-- Repeat similar structure for Active and Interview cards with different icons/colors -->
      <v-col cols="12" md="4">
        <v-card variant="outlined" class="fill-height pa-2">
          <v-card-item>
            <template v-slot:prepend>
              <v-icon color="info" size="x-large"
                >mdi-chart-line-variant</v-icon
              >
            </template>
            <v-card-title class="text-subtitle-1 font-weight-medium"
              >Active Applications</v-card-title
            >
          </v-card-item>
          <v-card-text class="text-h4 text-center pb-4">
            <v-progress-circular
              v-if="loading"
              indeterminate
              color="info"
              size="small"
            ></v-progress-circular>
            <span v-else>{{ activeApplications.length }}</span>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card variant="outlined" class="fill-height pa-2">
          <v-card-item>
            <template v-slot:prepend>
              <v-icon color="success" size="x-large">mdi-account-voice</v-icon>
            </template>
            <v-card-title class="text-subtitle-1 font-weight-medium"
              >Interview Stage</v-card-title
            >
          </v-card-item>
          <v-card-text class="text-h4 text-center pb-4">
            <v-progress-circular
              v-if="loading"
              indeterminate
              color="success"
              size="small"
            ></v-progress-circular>
            <span v-else>{{ interviewApplications.length }}</span>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Recent Applications Table Card -->
      <v-col cols="12">
        <v-card flat class="mt-6">
          <!-- Flat card -->
          <v-card-title class="d-flex align-center pa-4">
            <span class="text-h6 font-weight-regular">Recent Activity</span>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              size="small"
              to="/applications"
              variant="text"
              append-icon="mdi-arrow-right"
            >
              View All
            </v-btn>
          </v-card-title>
          <v-divider></v-divider>
          <v-card-text class="pa-0">
            <!-- Apply similar table styles as ApplicationListView -->
            <v-data-table
              :headers="headers"
              :items="recentApplications"
              :loading="loading"
              :items-per-page="5"
              item-value="id"
              density="comfortable"
              hover
            >
              <!-- Copy relevant <template v-slot:[`item.*`]> slots from ApplicationListView -->
              <!-- Example: -->
              <template v-slot:[`item.company`]="{ item }">
                <div class="font-weight-medium">{{ item.company || "-" }}</div>
              </template>
              <template v-slot:[`item.status`]="{ item }">
                <v-chip
                  :color="getStatusColor(item.status)"
                  size="small"
                  variant="tonal"
                  label
                >
                  {{ item.status }}
                </v-chip>
              </template>
              <template v-slot:[`item.applied_date`]="{ item }">
                <span class="text-grey-darken-1">{{
                  formatDate(item.applied_date)
                }}</span>
              </template>
              <template v-slot:[`item.date_posted`]="{ item }">
                <span class="text-grey-darken-1">{{
                  formatDate(item.date_posted)
                }}</span>
              </template>
              <template v-slot:[`item.linkedin_url`]="{ item }">
                <!-- LinkedIn Button -->
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
                <!-- Edit button only -->
                <v-tooltip location="top" text="View/Edit Application">
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
                    </v-btn>
                  </template>
                </v-tooltip>
              </template>
              <!-- Loading / No Data -->
              <template v-slot:loading>
                <v-skeleton-loader type="table-tbody@5"></v-skeleton-loader>
              </template>
              <template v-slot:no-data>
                <div class="text-center pa-4 text-grey">
                  No recent activity.
                </div>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </main-layout>
</template>

<script>
// ... (script remains largely the same, ensure computed/methods/headers are correct)
import { mapState, mapActions } from "vuex";
import MainLayout from "@/layouts/MainLayout.vue";

export default {
  name: "DashboardView",
  components: { MainLayout },
  data() {
    return {
      headers: [
        // Adjust keys/titles as needed, align actions end
        {
          title: "Company",
          key: "company",
          align: "start",
          sortable: false,
          minWidth: "150px",
        },
        {
          title: "Position",
          key: "title",
          align: "start",
          sortable: false,
          minWidth: "200px",
        },
        // { title: "Location", key: "location", align: 'start', sortable: false }, // Maybe hide location on dashboard
        {
          title: "Applied",
          key: "applied_date",
          align: "start",
          sortable: false,
          minWidth: "120px",
        },
        {
          title: "Status",
          key: "status",
          align: "center",
          sortable: false,
          minWidth: "120px",
        },
        {
          title: "LinkedIn",
          key: "linkedin_url",
          align: "center",
          sortable: false,
        },
        { title: "Actions", key: "actions", align: "end", sortable: false },
      ],
    };
  },
  computed: {
    // Map state from the 'applications' Vuex module
    ...mapState("applications", ["applications", "loading", "error"]), // Added error mapping too

    // Other computed properties that depend on the mapped state
    recentApplications() {
      // Defensive check: ensure applications is an array before processing
      if (!Array.isArray(this.applications)) {
        return [];
      }
      return [...this.applications]
        .sort((a, b) => {
          const dateA = a.created_at ? new Date(a.created_at).getTime() : 0;
          const dateB = b.created_at ? new Date(b.created_at).getTime() : 0;
          return dateB - dateA; // Descending order
        })
        .slice(0, 5); // Show top 5
    },
    activeApplications() {
      // Defensive check
      if (!Array.isArray(this.applications)) {
        return [];
      }
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
      // Defensive check
      if (!Array.isArray(this.applications)) {
        return [];
      }
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
    // ... mapActions, formatDate, getStatusColor ...
    ...mapActions("applications", ["fetchApplications"]),
    formatDate(dateString) {
      if (!dateString) return "–";
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return "Invalid";
        return date.toLocaleDateString(undefined, {
          month: "short",
          day: "numeric",
        }); // Shorter format for dashboard
      } catch (e) {
        return "Invalid";
      }
    },
    getStatusColor(status) {
      /* ... colors ... */
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
  },
  created() {
    // Fetch if applications state is not yet initialized (null/undefined)
    // or if it's an empty array.
    if (!this.applications || this.applications.length === 0) {
      console.log("Dashboard created: Fetching applications..."); // Optional debug log
      this.fetchApplications();
    } else {
      console.log("Dashboard created: Applications already loaded."); // Optional debug log
    }
  },
};
</script>

<style scoped>
.v-card.fill-height {
  display: flex;
  flex-direction: column;
  justify-content: space-between; /* Helps align content vertically */
}
.v-card-item {
  padding-bottom: 8px; /* Reduce space below title area */
}
.v-card-text.text-center {
  padding-top: 0; /* Reduce space above metric */
}
:deep(.v-data-table-header__content span) {
  font-weight: 500;
  color: #424242;
}
:deep(td:last-child) {
  text-align: right;
}
</style>
