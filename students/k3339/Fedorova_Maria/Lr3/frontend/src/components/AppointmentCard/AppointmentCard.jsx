import { useState } from "react";

import "./AppointmentCard.scss";

function AppointmentCard({ appointment, onPay, onDiagnose }) {
  const isBooking = !appointment.diagnosis;
  const [open, setOpen] = useState(false);
  const [diagnosis, setDiagnosis] = useState("");
  const [condition, setCondition] = useState("");
  const [recommendations, setRecommendations] = useState("");
  const [saving, setSaving] = useState(false);

  async function handleSave(event) {
    event.preventDefault();
    if (!onDiagnose) {
      return;
    }
    setSaving(true);
    try {
      await onDiagnose(appointment.id, {
        diagnosis,
        condition,
        recommendations,
      });
      setOpen(false);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="card appointment-card">
      <div className="appointment-main">
        <div className="card-title">{appointment.patient_name}</div>
        <div className="card-description">
          {appointment.doctor_name} · {appointment.doctor_specialty}
        </div>
        <div className="appointment-meta">
          <span>{new Date(appointment.visited_at).toLocaleString("ru-RU")}</span>
          <span>{appointment.service_name}</span>
          <span>{appointment.cost} ₽</span>
        </div>
        <div className="appointment-diagnosis">
          {isBooking
            ? "Статус: запись на приём (ожидает осмотра)"
            : `Диагноз: ${appointment.diagnosis}`}
        </div>
        {!isBooking && appointment.condition && (
          <div className="appointment-diagnosis">
            Состояние: {appointment.condition}
          </div>
        )}

        {isBooking && onDiagnose && open && (
          <form className="diagnose-form" onSubmit={handleSave}>
            <div className="form-group">
              <div className="form-label">Диагноз</div>
              <input
                className="input"
                value={diagnosis}
                onChange={(event) => setDiagnosis(event.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <div className="form-label">Состояние</div>
              <input
                className="input"
                value={condition}
                onChange={(event) => setCondition(event.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <div className="form-label">Рекомендации</div>
              <input
                className="input"
                value={recommendations}
                onChange={(event) => setRecommendations(event.target.value)}
              />
            </div>
            <div className="diagnose-actions">
              <button className="button button-primary" type="submit" disabled={saving}>
                Сохранить осмотр
              </button>
              <button
                className="button button-secondary"
                type="button"
                onClick={() => setOpen(false)}
              >
                Отмена
              </button>
            </div>
          </form>
        )}
      </div>

      <div className="appointment-actions">
        {isBooking && <span className="status status-pending">Запись</span>}
        <span
          className={
            appointment.is_paid ? "status status-confirmed" : "status status-pending"
          }
        >
          {appointment.is_paid ? "Оплачено" : "Не оплачено"}
        </span>

        {isBooking && onDiagnose && !open && (
          <button
            className="button button-primary"
            type="button"
            onClick={() => setOpen(true)}
          >
            Внести диагноз
          </button>
        )}

        {!appointment.is_paid && onPay && (
          <button
            className="button button-primary"
            type="button"
            onClick={() => onPay(appointment.id)}
          >
            Оплатить
          </button>
        )}
      </div>
    </div>
  );
}

export default AppointmentCard;
