import { createRouter, createWebHistory } from 'vue-router'

const Login = () => import('@/views/LogIn.vue')
const MainLayout = () => import('@/layouts/MainLayout.vue')
const Users = () => import('@/views/Users.vue')
const OverallHistory = () => import('@/views/OverallHistory.vue')

const routes = [
  {
    path: '/',
    redirect: '/admin-login',
  },
  {
    path: '/admin-login',
    name: 'LogIn',
    component: Login,
  },
  {
    path: '/app',
    component: MainLayout,
    children: [
      {
        path: 'users',
        name: 'Users',
        component: Users,
        meta: { requiresAuth: true }
      },
      {
        path: 'history',
        name: 'OverallHistory',
        component: OverallHistory,
        meta: { requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
