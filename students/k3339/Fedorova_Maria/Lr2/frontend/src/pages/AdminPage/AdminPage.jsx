import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import api from "../../api";
import { useAuth } from "../../context/AuthContext/AuthContext";

import "./AdminPage.scss";

function AdminPage() {
  const { user, loading: authLoading } = useAuth();
  const [reservations, setReservations] = useState([]);
  const [soldTours, setSoldTours] = useState([]);
  const [loading, setLoading] = useState(true);

  async function loadData() {
    try {
      const [reservationsResponse, soldResponse] = await Promise.all([
        api.get("/admin/reservations/"),
        api.get("/admin/stats/sold-by-country/"),
      ]);

      
      setReservations(
        reservationsResponse.data.results ?? reservationsResponse.data,
      );
      setSoldTours(soldResponse.data);
    } finally {
      setLoading(false);
    }
  }

  async function confirmReservation(id) {
    await api.patch(`/admin/reservations/${id}/confirm/`);
    await loadData();
  }

  useEffect(() => {
    if (user?.is_staff) {
      loadData();
    }
  }, [user]);

  if (authLoading) {
    return (
      <div className="page">
        <div className="page-subtitle">Загрузка...</div>
      </div>
    );
  }

  if (!user?.is_staff) {
    return <Navigate to="/" replace />;
  }

  if (loading) {
    return (
      <div className="page">
        <div className="page-subtitle">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">Панель администратора</div>
        <div className="page-subtitle">
          Подтверждайте бронирования и смотрите проданные туры по странам.
        </div>
      </div>

      <div className="section-title">Бронирования</div>

      {reservations.length === 0 ? (
        <div className="page-subtitle">Бронирований нет.</div>
      ) : (
        <div className="reservations-list admin-reservations">
          {reservations.map((reservation) => (
            <div className="card reservation-card" key={reservation.id}>
              <div>
                <div className="card-title">{reservation.tour_name}</div>
                <div className="card-description" style={{ marginTop: 8 }}>
                  Пользователь: {reservation.user.username}
                </div>
                <div style={{ marginTop: 14 }}>
                  <div
                    className={`status ${
                      reservation.is_confirmed
                        ? "status-confirmed"
                        : "status-pending"
                    }`}
                  >
                    {reservation.is_confirmed
                      ? "Подтверждено"
                      : "Ожидает подтверждения"}
                  </div>
                </div>
              </div>

              <div className="reservation-actions">
                {!reservation.is_confirmed && (
                  <button
                    className="button button-primary"
                    onClick={() => confirmReservation(reservation.id)}
                  >
                    Подтвердить
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="section-title">Проданные туры по странам</div>

      {soldTours.length === 0 ? (
        <div className="page-subtitle">Подтверждённых продаж пока нет.</div>
      ) : (
        <div className="table-card">
          <table className="table">
            <thead>
              <tr>
                <th>Страна</th>
                <th>Тур</th>
                <th>Клиент</th>
                <th>Даты</th>
              </tr>
            </thead>
            <tbody>
              {soldTours.map((item, index) => (
                <tr key={`${item.country}-${item.tour}-${item.user}-${index}`}>
                  <td>{item.country}</td>
                  <td>{item.tour}</td>
                  <td>{item.user}</td>
                  <td>
                    {item.start_date} — {item.end_date}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default AdminPage;
