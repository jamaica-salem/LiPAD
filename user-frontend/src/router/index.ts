import { createRouter, createWebHistory } from 'vue-router'
import LogIn from '@/views/LogIn.vue'
import LicensePlateUpload from '@/views/LicensePlateUpload.vue'
import NavbarLayout from '@/layouts/NavbarLayout.vue'
import LoadingPage from '@/views/LoadingPage.vue'
import FailurePage from '@/views/FailurePage.vue'

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
      },
      {
        path: '/loading',
        name: 'LoadingPage',
        component: LoadingPage,
      },
            {
        path: '/failed',
        name: 'FailurePage',
        component: FailurePage,
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
