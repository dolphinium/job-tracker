// job-tracker-frontend/src/layouts/MainLayout.vue
<template>
  <v-app>
    <!-- Use flat or low elevation for a cleaner look -->
    <v-app-bar app color="white" flat border>
      <!-- Changed color, added flat & border -->
      <v-app-bar-nav-icon
        @click="drawer = !drawer"
        color="grey-darken-1"
      ></v-app-bar-nav-icon>
      <v-toolbar-title class="font-weight-medium text-grey-darken-3">
        <!-- Adjusted font weight/color -->
        Job Application Tracker
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <!-- Add tooltip for clarity -->
      <v-tooltip location="bottom">
        <template v-slot:activator="{ props }">
          <v-btn
            v-if="isAuthenticated"
            icon
            @click="logout"
            v-bind="props"
            color="grey-darken-1"
          >
            <v-icon>mdi-logout-variant</v-icon>
            <!-- Slightly different icon -->
          </v-btn>
        </template>
        <span>Logout</span>
      </v-tooltip>
    </v-app-bar>

    <v-navigation-drawer v-model="drawer" app>
      <!-- Optional: User Info -->
      <v-list-item
        v-if="user"
        :title="user.username"
        :subtitle="user.email"
        class="pa-3"
      >
        <template v-slot:prepend>
          <v-avatar color="primary" size="small" class="mr-3">
            <span class="white--text text-h6">{{
              user.username ? user.username[0].toUpperCase() : "?"
            }}</span>
          </v-avatar>
        </template>
      </v-list-item>
      <v-divider v-if="user"></v-divider>

      <!-- Navigation Items -->
      <v-list nav density="compact">
        <!-- Added nav & density -->
        <v-list-item
          v-for="item in navItems"
          :key="item.title"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
          exact
          active-class="primary--text"
          color="primary"
        ></v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-main class="bg-grey-lighten-4">
      <!-- Lighter background for main area -->
      <!-- Add consistent padding around the content -->
      <v-container fluid class="pa-4 pa-md-6">
        <slot></slot>
        <!-- Router view content will go here -->
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { mapGetters, mapActions, mapState } from "vuex";

export default {
  name: "MainLayout",
  data() {
    return {
      drawer: null, // Let Vuetify handle initial state based on screen size if needed
      navItems: [
        { title: "Dashboard", icon: "mdi-view-dashboard-outline", to: "/" },
        {
          title: "Applications",
          icon: "mdi-briefcase-search-outline",
          to: "/applications",
        },
        {
          title: "New Application",
          icon: "mdi-plus-box-outline",
          to: "/applications/new",
        },
        {
          title: "GitHub Projects",
          icon: "mdi-github",
          to: "/github",
        },
      ],
    };
  },
  computed: {
    ...mapGetters("auth", ["isAuthenticated"]),
    ...mapState("auth", ["user"]), // Get user info for the drawer
  },
  methods: {
    ...mapActions("auth", ["logout", "fetchUser"]), // Add fetchUser
  },
  created() {
    // Attempt to fetch user info when the layout is created if authenticated
    if (this.isAuthenticated && !this.user) {
      this.fetchUser();
    }
  },
};
</script>

<style scoped>
/* Add specific styles if needed, but try to rely on Vuetify classes */
.v-main {
  /* Ensures content starts below app bar */
  padding-top: 64px; /* Adjust if app bar height changes */
}
.v-navigation-drawer .v-list-item-title {
  font-size: 0.95rem; /* Slightly smaller nav text */
}
</style>
