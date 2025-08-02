import { createRouter, createWebHistory } from 'vue-router'
import LogIn from '@/views/LogIn.vue'
import LicensePlateUpload from '@/views/LicensePlateUpload.vue'
import NavbarLayout from '@/layouts/NavbarLayout.vue'

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
    path: '/upload',
    component: NavbarLayout,
    children: [
      {
        path: '',
        name: 'LicensePlateUpload',
        component: LicensePlateUpload,
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
