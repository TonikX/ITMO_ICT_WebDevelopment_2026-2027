import http from "./http"

export const authApi = {
  login: (payload) => http.post("/auth/token/login/", payload),
  logout: () => http.post("/auth/token/logout/"),
  register: (payload) => http.post("/auth/users/", payload),
  me: () => http.get("/auth/users/me/"),
  updateMe: (payload) => http.patch("/auth/users/me/", payload),
}

export const clinicApi = {
  doctors: () => http.get("/api/doctors/"),
  doctor: (id) => http.get(`/api/doctors/${id}/`),
  doctorPatients: (id) => http.get(`/api/doctors/${id}/patients/`),
  createDoctor: (payload) => http.post("/api/doctors/", payload),
  updateDoctor: (id, payload) => http.patch(`/api/doctors/${id}/`, payload),
  deleteDoctor: (id) => http.delete(`/api/doctors/${id}/`),

  patients: () => http.get("/api/patients/"),
  patient: (id) => http.get(`/api/patients/${id}/`),
  createPatient: (payload) => http.post("/api/patients/", payload),
  updatePatient: (id, payload) => http.patch(`/api/patients/${id}/`, payload),
  deletePatient: (id) => http.delete(`/api/patients/${id}/`),

  medicalCards: () => http.get("/api/medical-cards/"),
  medicalCardVisits: (id) => http.get(`/api/medical-cards/${id}/visits/`),

  visits: () => http.get("/api/visits/"),
  createVisit: (payload) => http.post("/api/visits/", payload),
  deleteVisit: (id) => http.delete(`/api/visits/${id}/`),

  cabinets: () => http.get("/api/cabinets/"),
  priceList: () => http.get("/api/price-list/"),
  schedules: () => http.get("/api/schedules/"),

  analyticsOtolaryngology: () => http.get("/api/analytics/otolaryngology-patients/"),
  analyticsTreatmentSums: () => http.get("/api/analytics/treatment-sums/"),
  analyticsVisitsByDate: () => http.get("/api/analytics/visits-by-date/"),
  analyticsPaidPatients: () => http.get("/api/analytics/paid-patients/"),
  analyticsDoctorsByDate: (date) =>
    http.get("/api/analytics/doctors-by-date/", { params: { date } }),
  analyticsDoctorPatients: (doctorId) =>
    http.get(`/api/analytics/doctor/${doctorId}/patients/`),
  analyticsDoctorPeriod: (from, to) =>
    http.get("/api/analytics/doctor-period-report/", { params: { from, to } }),
}
