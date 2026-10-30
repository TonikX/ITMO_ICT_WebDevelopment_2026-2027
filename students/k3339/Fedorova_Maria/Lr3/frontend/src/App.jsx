import { BrowserRouter, Route, Routes } from "react-router-dom";

import Navbar from "./components/Navbar/Navbar";
import AnalyticsPage from "./pages/AnalyticsPage/AnalyticsPage";
import AppointmentsPage from "./pages/AppointmentsPage/AppointmentsPage";
import DoctorDetailPage from "./pages/DoctorDetailPage/DoctorDetailPage";
import DoctorsPage from "./pages/DoctorsPage/DoctorsPage";
import LoginPage from "./pages/LoginPage/LoginPage";
import PatientsPage from "./pages/PatientsPage/PatientsPage";
import ProfilePage from "./pages/ProfilePage/ProfilePage";
import RegisterPage from "./pages/RegisterPage/RegisterPage";

function App() {
  return (
    <BrowserRouter>
      <Navbar />

      <Routes>
        <Route path="/" element={<DoctorsPage />} />
        <Route path="/doctors/:id" element={<DoctorDetailPage />} />
        <Route path="/patients" element={<PatientsPage />} />
        <Route path="/appointments" element={<AppointmentsPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
