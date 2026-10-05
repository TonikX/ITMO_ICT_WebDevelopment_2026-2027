import { createRouter, createWebHistory } from "vue-router"
import Hello from "@/components/Hello.vue"
import Home from "@/views/Home.vue"
import Warriors from "@/views/Warriors.vue"

const routes = [
  { path: "/", component: Home },
  { path: "/hi", component: Hello },
  { path: "/warriors", component: Warriors },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
