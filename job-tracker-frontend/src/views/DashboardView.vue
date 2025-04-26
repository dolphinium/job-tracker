<template>
  <main-layout>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            Dashboard
            <v-spacer></v-spacer>
            <v-btn color="primary" to="/applications/new">
              <v-icon left>mdi-plus</v-icon>
              New Application
            </v-btn>
          </v-card-title>
          <v-card-text v-if="loading">
            <v-progress-circular
              indeterminate
              color="primary"
            ></v-progress-circular>
          </v-card-text>
          <v-card-text v-else>
            <v-row>
              <v-col cols="12" md="4">
                <v-card outlined>
                  <v-card-title class="primary--text"
                    >Total Applications</v-card-title
                  >
                  <v-card-text class="text-h4 text-center">
                    {{ applications.length }}
                  </v-card-text>
                </v-card>
              </v-col>

              <v-col cols="12" md="4">
                <v-card outlined>
                  <v-card-title class="info--text"
                    >Active Applications</v-card-title
                  >
                  <v-card-text class="text-h4 text-center">
                    {{ activeApplications.length }}
                  </v-card-text>
                </v-card>
              </v-col>

              <v-col cols="12" md="4">
                <v-card outlined>
                  <v-card-title class="success--text"
                    >Interview Stage</v-card-title
                  >
                  <v-card-text class="text-h4 text-center">
                    {{ interviewApplications.length }}
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>

            <v-divider class="my-5"></v-divider>

            <h3 class="text-h5 mb-3">Recent Applications</h3>
            <v-data-table
              :headers="headers"
              :items="recentApplications"
              :items-per-page="5"
              class="elevation-1"
            >
              <template v-slot:[`item.status`]="{ item }">
                <v-chip
                  :color="getStatusColor(item.status)"
                  text-color="white"
                  small
                >
                  {{ item.status }}
                </v-chip>
              </template>
              <template v-slot:[`item.actions`]="{ item }">
                <v-btn
                  icon
                  small
                  color="primary"
                  :to="`/applications/${item.id}`"
                >
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
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
      headers: [
        { text: "Company", value: "company" },
        { text: "Position", value: "title" },
        { text: "Status", value: "status" },
        { text: "Applied Date", value: "applied_date" },
        { text: "Actions", value: "actions", sortable: false },
      ],
    };
  },
  computed: {
    ...mapState("applications", ["applications", "loading"]),
    recentApplications() {
      return [...this.applications]
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 5);
    },
    activeApplications() {
      return this.applications.filter(
        (app) => !["Rejected", "Withdrawn", "Accepted"].includes(app.status)
      );
    },
    interviewApplications() {
      return this.applications.filter((app) =>
        ["Interview", "Technical Test", "Final Interview"].includes(app.status)
      );
    },
  },
  methods: {
    ...mapActions("applications", ["fetchApplications"]),
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
  },
  created() {
    this.fetchApplications();
  },
};
</script>
