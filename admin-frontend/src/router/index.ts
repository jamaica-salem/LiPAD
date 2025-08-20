import { createRouter, createWebHistory } from "vue-router";
import Login from "@/views/Login.vue";
import MainLayout from "@/layouts/MainLayout.vue";
import Users from "@/views/Users.vue";
import History from "@/views/OverallHistory.vue";
import { useAuth } from "@/composables/useAuth"; // we'll create this

const routes = [
  {
    path: "/admin-login",
    name: "Login",
    component: Login,
    meta: { guestOnly: true }, // only for non-logged-in users
  },

  {
    path: "/app",
    component: MainLayout,
    meta: { requiresAuth: true }, // protect all child routes
    children: [
      { path: "users", name: "Users", component: Users },
      { path: "history", name: "OverallHistory", component: History },
      { path: "", redirect: { name: "OverallHistory" } }, // default redirect
    ],
  },

  // fallback
  { path: "/:pathMatch(.*)*", redirect: "/app" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 🔒 Global Navigation Guards
router.beforeEach((to, from, next) => {
  const auth = useAuth();

  if (auth.loading) {
    // still checking session from server
    return next();
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next({ name: "Login" });
  }

  if (to.meta.guestOnly && auth.isAuthenticated) {
    return next({ path: "/app" });
  }

  return next();
});

export default router;
