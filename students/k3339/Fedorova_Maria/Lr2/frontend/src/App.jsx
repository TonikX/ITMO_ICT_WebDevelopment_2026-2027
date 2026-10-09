import { BrowserRouter, Route, Routes } from "react-router-dom";

import Navbar from "./components/Navbar/Navbar";
import AdminPage from "./pages/AdminPage/AdminPage";
import LoginPage from "./pages/LoginPage/LoginPage";
import RegisterPage from "./pages/RegisterPage/RegisterPage";
import ReservationsPage from "./pages/ReservationsPage/ReservationsPage";
import TourDetailPage from "./pages/TourDetailPage/TourDetailPage";
import ToursPage from "./pages/ToursPage/ToursPage";

function App() {
  return (
    <BrowserRouter>
      <Navbar />

      <Routes>
        <Route path="/" element={<ToursPage />} />
        <Route path="/tours/:id" element={<TourDetailPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/reservations" element={<ReservationsPage />} />
        <Route path="/admin" element={<AdminPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
