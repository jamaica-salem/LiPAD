// src/main.ts
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { initAuth } from '@/composables/useAuth'
import './index.css'

async function bootstrap() {
  try {
    await initAuth()
  } catch (err) {
    console.error('Auth init failed:', err)
  } finally {
    createApp(App).use(router).mount('#app')
  }
}

bootstrap()
