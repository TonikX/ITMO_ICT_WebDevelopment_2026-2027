import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import AccountView from '@/views/AccountView.vue'
import ResourceView from '@/views/ResourceView.vue'
import AnalyticsView from '@/views/AnalyticsView.vue'
import ReportView from '@/views/ReportView.vue'

const routes = [
  { path: '/', redirect: '/r/newspapers' },
  { path: '/login', component: LoginView, meta: { guest: true } },
  { path: '/register', component: RegisterView, meta: { guest: true } },
  { path: '/account', component: AccountView },
  { path: '/r/:name', component: ResourceView, props: true },
  { path: '/analytics', component: AnalyticsView },
  { path: '/report', component: ReportView },
]

const router = createRouter({ history: createWebHistory(), routes })

// без токена пускаем только на вход и регистрацию
router.beforeEach((to) => {
  if (!to.meta.guest && !useAuthStore().token) return '/login'
})

export default router
