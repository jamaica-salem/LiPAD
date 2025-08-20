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
      { path: '/History', name: 'History', component: History, meta: { requiresAuth: true } },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Global guard - follows Admin pattern:
// - if auth.loading -> allow (initAuth hasn't completed yet; createApp mount waits for initAuth)
// - if route requiresAuth and not authenticated -> redirect to login
router.beforeEach((to, from, next) => {
  const auth = useAuth();

  if (auth.loading) {
    // still checking session from server
    return next();
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next({ name: 'Login' });
  }

  return next();
});

export default router;
