// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router';
import LogIn from '@/views/LogIn.vue';
import LicensePlateUpload from '@/views/LicensePlateUpload.vue';
import NavbarLayout from '@/layouts/NavbarLayout.vue';
import MainLayout from '@/layouts/MainLayout.vue';
import LoadingPage from '@/views/LoadingPage.vue';
import FailurePage from '@/views/FailurePage.vue';
import Result from '@/views/Result.vue';
import History from '@/views/History.vue';
import { useAuth } from '@/composables/useAuth';

const routes = [
  { path: '/', redirect: '/lipad/login' },
  { path: '/lipad/login', name: 'Login', component: LogIn },
  {
    path: '/',
    component: NavbarLayout,
    children: [
      { path: '/upload', name: 'LicensePlateUpload', component: LicensePlateUpload, meta: { requiresAuth: true } },
      { path: '/loading', name: 'LoadingPage', component: LoadingPage, meta: { requiresAuth: true } },
      { path: '/failed', name: 'FailurePage', component: FailurePage, meta: { requiresAuth: true } },
    ],
  },
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '/result', name: 'Result', component: Result, meta: { requiresAuth: true } },
      { path: '/history', name: 'History', component: History, meta: { requiresAuth: true } },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// --- Global Route Guard ---
router.beforeEach((to, from, next) => {
  const auth = useAuth();

  if (auth.loading) {
    // still checking session from server
    return next();
  }

  // If route requires authentication and user is not logged in
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next({ name: 'Login' });
  }

  // If user is already logged in, prevent going to login page
  if (to.name === 'Login' && auth.isAuthenticated) {
    // redirect to default dashboard page (inside MainLayout)
    return next({ name: 'LicensePlateUpload' });
  }

  return next();
});

export default router;
