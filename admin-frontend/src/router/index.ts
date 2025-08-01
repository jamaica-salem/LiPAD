import { createRouter, createWebHistory } from 'vue-router'

const Login = () => import('@/views/Login.vue')
const MainLayout = () => import('@/layouts/MainLayout.vue')
const Users = () => import('@/views/Users.vue')
const OverallHistory = () => import('@/views/OverallHistory.vue')

const routes = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/login',
    name: 'Login',
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
      },
      {
        path: 'history',
        name: 'OverallHistory',
        component: OverallHistory,
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
