import { useEffect, useState } from "react";

import EditReservationModal from "../../components/EditReservationModal/EditReservationModal";
import ReservationCard from "../../components/ReservationCard/ReservationCard";
import api from "../../api";

import "./ReservationsPage.scss";

function ReservationsPage() {
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingReservation, setEditingReservation] = useState(null);
  const [message, setMessage] = useState("");

  async function loadReservations() {
    try {
      
      const response = await api.get("/reservations/");
      setReservations(response.data.results ?? response.data);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id) {
    setMessage("");
    await api.delete(`/reservations/${id}/`);
    await loadReservations();
  }

  async function handleDatesChange(reservationId, startDate, endDate) {
    await api.patch(`/reservations/${reservationId}/`, {
      start_date: startDate,
      end_date: endDate,
    });

    await loadReservations();
    setMessage(
      "Даты изменены. Бронирование отправлено на повторное подтверждение.",
    );
  }

  useEffect(() => {
    loadReservations();
  }, []);

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
        <div className="page-title">Мои бронирования</div>
        <div className="page-subtitle">
          Управляйте своими заявками: меняйте даты поездки или удаляйте бронь.
        </div>
      </div>

      {message && <div className="message message-success">{message}</div>}

      {reservations.length === 0 ? (
        <div className="page-subtitle">У вас пока нет бронирований.</div>
      ) : (
        <div className="reservations-list">
          {reservations.map((reservation) => (
            <ReservationCard
              key={reservation.id}
              reservation={reservation}
              onEdit={setEditingReservation}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      <EditReservationModal
        reservation={editingReservation}
        isOpen={Boolean(editingReservation)}
        onClose={() => setEditingReservation(null)}
        onSave={handleDatesChange}
      />
    </div>
  );
}

export default ReservationsPage;
