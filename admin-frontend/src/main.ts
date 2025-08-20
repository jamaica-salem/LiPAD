// src/main.ts
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { initAuth } from "@/composables/useAuth";
import "./index.css"  

async function bootstrap() {
  // Initialize authentication (sets state.admin/isAuthenticated)
  try {
    await initAuth();
  } catch (err) {
    // failed to init auth — app still loads but treats user as unauthenticated
    console.error("Auth init failed:", err);
  } finally {
    createApp(App).use(router).mount("#app");
  }
}

bootstrap();
