import "./ReservationCard.scss";

function ReservationCard({ reservation, onEdit, onDelete }) {
  return (
    <div className="card reservation-card">
      <div>
        <div className="card-title">{reservation.tour_name}</div>

        <div className="card-description">
          Создано: {new Date(reservation.created_at).toLocaleString()}
        </div>

        {reservation.start_date && reservation.end_date && (
          <div className="card-description">
            Даты: {reservation.start_date} — {reservation.end_date}
          </div>
        )}

        <div
          className={
            reservation.is_confirmed
              ? "status status-confirmed"
              : "status status-pending"
          }
          style={{ marginTop: 14 }}
        >
          {reservation.is_confirmed ? "Подтверждено" : "Ожидает подтверждения"}
        </div>
      </div>

      <div className="reservation-actions">
        <button
          className="button button-secondary"
          onClick={() => onEdit(reservation)}
        >
          Редактировать
        </button>

        <button
          className="button button-danger"
          onClick={() => onDelete(reservation.id)}
        >
          Удалить
        </button>
      </div>
    </div>
  );
}

export default ReservationCard;
