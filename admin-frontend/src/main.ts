import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './index.css'

router.beforeEach((to, from, next) => {
  const token = sessionStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

createApp(App).use(router).mount('#app')
