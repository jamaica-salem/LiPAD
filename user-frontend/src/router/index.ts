  import { createRouter, createWebHistory } from 'vue-router'
  import LogIn from '@/views/LogIn.vue'
  import LicensePlateUpload from '@/views/LicensePlateUpload.vue'
  import NavbarLayout from '@/layouts/NavbarLayout.vue'
  import MainLayout from '@/layouts/MainLayout.vue' 
  import LoadingPage from '@/views/LoadingPage.vue'
  import FailurePage from '@/views/FailurePage.vue'
  import Result from '@/views/Result.vue'
  import History from '@/views/History.vue'

  const routes = [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'Login',
      component: LogIn,
    },
    {
      path: '/',
      component: NavbarLayout,
      children: [
        {
          path: '/upload',
          name: 'LicensePlateUpload',
          component: LicensePlateUpload,
          meta: { requiresAuth: true }
        },
        {
          path: '/loading',
          name: 'LoadingPage',
          component: LoadingPage,
          meta: { requiresAuth: true }
        },
        {
          path: '/failed',
          name: 'FailurePage',
          component: FailurePage,
          meta: { requiresAuth: true }
        },
      ],
    },
    {
      path: '/',
      component: MainLayout, 
      children: [
        {
          path: '/result',
          name: 'Result',
          component: Result,
          meta: { requiresAuth: true }
        },
        {
          path: '/History',
          name: 'History',
          component: History,
          meta: { requiresAuth: true }
        },
      ],
    },
  ]

  const router = createRouter({
    history: createWebHistory(),
    routes,
  })

  export default router
