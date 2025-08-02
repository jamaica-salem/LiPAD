// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

import LogIn from '@/views/LogIn.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LogIn,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
