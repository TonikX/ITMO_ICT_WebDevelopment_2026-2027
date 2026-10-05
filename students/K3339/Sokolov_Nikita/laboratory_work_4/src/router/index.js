import { createRouter, createWebHistory } from "vue-router"
import { useAuthStore } from "@/stores/auth"

const routes = [
  {
    path: "/login",
    name: "login",
    component: () => import("@/views/LoginView.vue"),
    meta: { guest: true },
  },
  {
    path: "/register",
    name: "register",
    component: () => import("@/views/RegisterView.vue"),
    meta: { guest: true },
  },
  {
    path: "/",
    component: () => import("@/layouts/MainLayout.vue"),
    meta: { requiresAuth: true },
    children: [
      { path: "", name: "home", component: () => import("@/views/HomeView.vue") },
      { path: "profile", name: "profile", component: () => import("@/views/ProfileView.vue") },
      { path: "doctors", name: "doctors", component: () => import("@/views/DoctorsView.vue") },
      {
        path: "doctors/:id",
        name: "doctor-detail",
        component: () => import("@/views/DoctorDetailView.vue"),
      },
      { path: "patients", name: "patients", component: () => import("@/views/PatientsView.vue") },
      {
        path: "patients/:id",
        name: "patient-detail",
        component: () => import("@/views/PatientDetailView.vue"),
      },
      { path: "visits", name: "visits", component: () => import("@/views/VisitsView.vue") },
      {
        path: "medical-cards",
        name: "medical-cards",
        component: () => import("@/views/MedicalCardsView.vue"),
      },
      { path: "cabinets", name: "cabinets", component: () => import("@/views/CabinetsView.vue") },
      {
        path: "price-list",
        name: "price-list",
        component: () => import("@/views/PriceListView.vue"),
      },
      {
        path: "schedules",
        name: "schedules",
        component: () => import("@/views/SchedulesView.vue"),
      },
      {
        path: "analytics",
        name: "analytics",
        component: () => import("@/views/AnalyticsView.vue"),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (auth.token && !auth.user) {
    await auth.fetchMe()
  }
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: "login", query: { redirect: to.fullPath } }
  }
  if (to.meta.guest && auth.isAuthenticated) {
    return { name: "home" }
  }
  return true
})

export default router
