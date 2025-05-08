import { createRouter, createWebHistory } from "vue-router";
import DashboardView from "../views/DashboardView.vue";
import ApplicationListView from "../views/ApplicationListView.vue";
import ApplicationFormView from "../views/ApplicationFormView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import GitHubProjectsView from "../views/GitHubProjectsView.vue";
import store from "../store";

const routes = [
  {
    path: "/",
    name: "dashboard",
    component: DashboardView,
    meta: { requiresAuth: true },
  },
  {
    path: "/applications",
    name: "applications",
    component: ApplicationListView,
    meta: { requiresAuth: true },
  },
  {
    path: "/applications/new",
    name: "new-application",
    component: ApplicationFormView,
    meta: { requiresAuth: true },
  },
  {
    path: "/applications/:id",
    name: "edit-application",
    component: ApplicationFormView,
    meta: { requiresAuth: true },
  },
  {
    path: "/login",
    name: "login",
    component: LoginView,
  },
  {
    path: "/register",
    name: "register",
    component: RegisterView,
  },
  {
    path: "/github",
    name: "github-projects",
    component: GitHubProjectsView,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

// Navigation guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters["auth/isAuthenticated"];

  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next({ name: "login" });
    } else {
      next();
    }
  } else {
    if (isAuthenticated && (to.name === "login" || to.name === "register")) {
      next({ name: "dashboard" });
    } else {
      next();
    }
  }
});

export default router;
