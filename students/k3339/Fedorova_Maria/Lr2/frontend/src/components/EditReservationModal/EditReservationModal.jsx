import { useEffect, useState } from "react";

import "./EditReservationModal.scss";

function EditReservationModal({ reservation, isOpen, onClose, onSave }) {
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  useEffect(() => {
    if (reservation) {
      setStartDate(reservation.start_date || "");
      setEndDate(reservation.end_date || "");
    }
  }, [reservation]);

  if (!isOpen || !reservation) {
    return null;
  }

  async function handleSubmit(event) {
    event.preventDefault();

    await onSave(reservation.id, startDate, endDate);
    onClose();
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(event) => event.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div className="modal-eyebrow">Редактирование бронирования</div>
            <div className="modal-title">{reservation.tour_name}</div>
          </div>

          <button className="modal-close" type="button" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="modal-tour-info">
          <div className="info-item">
            <div className="info-label">Тур</div>
            <div className="info-value">{reservation.tour_name}</div>
          </div>

          <div className="info-item">
            <div className="info-label">Статус</div>
            <div className="info-value">
              {reservation.is_confirmed
                ? "Подтверждено"
                : "Ожидает подтверждения"}
            </div>
          </div>

          <div className="info-item">
            <div className="info-label">Бронирование создано</div>
            <div className="info-value">
              {new Date(reservation.created_at).toLocaleString()}
            </div>
          </div>
        </div>

        <form className="form" onSubmit={handleSubmit}>
          <div className="modal-dates">
            <div className="form-group">
              <div className="form-label">Дата начала</div>
              <input
                className="input"
                type="date"
                value={startDate}
                onChange={(event) => setStartDate(event.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <div className="form-label">Дата окончания</div>
              <input
                className="input"
                type="date"
                value={endDate}
                onChange={(event) => setEndDate(event.target.value)}
                required
              />
            </div>
          </div>

          <div className="modal-actions">
            <button
              className="button button-secondary"
              type="button"
              onClick={onClose}
            >
              Отмена
            </button>

            <button className="button button-primary" type="submit">
              Сохранить изменения
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default EditReservationModal;
