import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import api from "../../api";
import { useAuth } from "../../context/AuthContext/AuthContext";

import "./DoctorDetailPage.scss";

function DoctorDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [doctor, setDoctor] = useState(null);
  const [services, setServices] = useState([]);
  const [serviceId, setServiceId] = useState("");
  const [visitedAt, setVisitedAt] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [bookError, setBookError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const [doctorRes, servicesRes] = await Promise.all([
          api.get(`/doctors/${id}/`),
          api.get("/services/"),
        ]);
        setDoctor(doctorRes.data);
        const list = servicesRes.data.results ?? servicesRes.data;
        const filtered = list.filter(
          (item) =>
            !item.specialty ||
            item.specialty
              .toLowerCase()
              .includes(doctorRes.data.specialty.toLowerCase().slice(0, 5)),
        );
        const options = filtered.length ? filtered : list;
        setServices(options);
        if (options[0]) {
          setServiceId(String(options[0].id));
        }
      } catch {
        setError("Не удалось загрузить карточку врача");
      }
    }

    load();
  }, [id]);

  async function handleBook(event) {
    event.preventDefault();
    setBookError("");
    setMessage("");

    if (!user) {
      navigate("/login");
      return;
    }
    if (!user.is_patient) {
      navigate("/profile");
      return;
    }

    try {
      await api.post("/appointments/", {
        doctor: Number(id),
        service: Number(serviceId),
        visited_at: visitedAt,
      });
      setMessage("Вы записаны на приём");
      setVisitedAt("");
    } catch {
      setBookError("Не удалось записаться. Проверьте дату и услугу.");
    }
  }

  if (error) {
    return (
      <div className="page">
        <div className="message message-error">{error}</div>
      </div>
    );
  }

  if (!doctor) {
    return (
      <div className="page">
        <div className="page-subtitle">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="page">
      <Link to="/" className="back-link">
        ← К списку врачей
      </Link>

      <div className="page-header">
        <div className="page-title">{doctor.full_name}</div>
        <div className="page-subtitle">{doctor.specialty}</div>
      </div>

      <div className="detail-grid">
        <div className="card">
          <div className="section-title">Сведения</div>
          <div className="info-item">
            <div className="info-label">Образование</div>
            <div className="info-value">{doctor.education}</div>
          </div>
          <div className="info-item">
            <div className="info-label">Дата рождения</div>
            <div className="info-value">{doctor.birth_date}</div>
          </div>
          <div className="info-item">
            <div className="info-label">Работает с</div>
            <div className="info-value">{doctor.work_start}</div>
          </div>
          <div className="info-item">
            <div className="info-label">Трудовой договор</div>
            <div className="info-value">
              {doctor.contract_number} от {doctor.contract_date}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="section-title">График</div>
          <div className="schedule-list">
            {doctor.schedules?.map((item) => (
              <div className="schedule-row" key={item.id}>
                <span>{item.weekday_display}</span>
                <span
                  className={
                    item.is_working ? "status status-confirmed" : "status status-pending"
                  }
                >
                  {item.is_working ? "Рабочий" : "Выходной"}
                </span>
              </div>
            ))}
          </div>
        </div>

        <form className="form-card form book-card" onSubmit={handleBook}>
          <div className="section-title">Записаться на приём</div>
          <div className="page-subtitle" style={{ marginTop: 0, marginBottom: 12 }}>
            {!user && "Войдите и оформите медкарту, чтобы записаться."}
            {user && !user.is_patient && !user.is_staff && !user.is_doctor && (
              <>Сначала оформите медкарту.</>
            )}
            {user?.is_patient && <>Выберите услугу и удобное время.</>}
            {(user?.is_staff || user?.is_doctor) && (
              <>Запись пациента создаётся в разделе «Приёмы».</>
            )}
          </div>

          <div className="form-group">
            <div className="form-label">Услуга</div>
            <select
              className="select"
              value={serviceId}
              onChange={(event) => setServiceId(event.target.value)}
              required
              disabled={!user?.is_patient}
            >
              {services.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name} — {item.price} ₽
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <div className="form-label">Дата и время</div>
            <input
              className="input"
              type="datetime-local"
              value={visitedAt}
              onChange={(event) => setVisitedAt(event.target.value)}
              required
              disabled={!user?.is_patient}
            />
          </div>

          {user?.is_patient ? (
            <button className="button button-primary" type="submit">
              Записаться
            </button>
          ) : !user ? (
            <Link className="button button-primary" to="/login">
              Войти, чтобы записаться
            </Link>
          ) : !user.is_staff && !user.is_doctor ? (
            <Link className="button button-primary" to="/profile">
              Оформить медкарту
            </Link>
          ) : null}

          {message && <div className="message message-success">{message}</div>}
          {bookError && <div className="message message-error">{bookError}</div>}
        </form>
      </div>
    </div>
  );
}

export default DoctorDetailPage;
