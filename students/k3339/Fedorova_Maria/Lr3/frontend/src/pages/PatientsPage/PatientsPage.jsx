import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import api from "../../api";
import { useAuth } from "../../context/AuthContext/AuthContext";

import "./PatientsPage.scss";

const emptyForm = {
  last_name: "",
  first_name: "",
  middle_name: "",
  birth_date: "",
  gender: "F",
  phone: "",
  address: "",
  passport: "",
  card_number: "",
};

function PatientsPage() {
  const { user, loading: authLoading } = useAuth();
  const [patients, setPatients] = useState([]);
  const [search, setSearch] = useState("");
  const [form, setForm] = useState(emptyForm);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function loadPatients() {
    const response = await api.get("/patients/", {
      params: { search: search.trim() || undefined },
    });
    setPatients(response.data.results ?? response.data);
  }

  useEffect(() => {
    if (user?.is_staff || user?.is_doctor) {
      loadPatients().catch(() => setError("Не удалось загрузить пациентов"));
    }
  }, [user]);

  async function handleCreate(event) {
    event.preventDefault();
    setMessage("");
    setError("");

    try {
      await api.post("/patients/", form);
      setForm(emptyForm);
      setMessage("Пациент добавлен");
      await loadPatients();
    } catch {
      setError("Проверьте поля формы");
    }
  }

  if (authLoading) {
    return (
      <div className="page">
        <div className="page-subtitle">Загрузка...</div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (!user.is_staff && !user.is_doctor) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">
          {user.is_staff ? "Пациенты" : "Мои пациенты"}
        </div>
        <div className="page-subtitle">
          {user.is_staff
            ? "Все медицинские карты клиники."
            : "Пациенты, которые были у вас на приёме."}
        </div>
      </div>

      <form
        className="filters"
        onSubmit={(event) => {
          event.preventDefault();
          loadPatients().catch(() => setError("Ошибка поиска"));
        }}
      >
        <div className="form-group">
          <div className="form-label">Поиск</div>
          <input
            className="input"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="ФИО, телефон, карта"
          />
        </div>
        <button className="button button-primary" type="submit">
          Найти
        </button>
      </form>

      <div className="patients-layout">
        <div className="patients-list">
          {patients.map((patient) => (
            <div className="card" key={patient.id}>
              <div className="card-title">{patient.full_name}</div>
              <div className="card-description">
                Карта {patient.card_number} · {patient.phone}
              </div>
              <div className="doctor-meta">
                <span>Дата рождения: {patient.birth_date}</span>
                <span>{patient.address}</span>
              </div>
            </div>
          ))}
          {patients.length === 0 && (
            <div className="page-subtitle">Пациентов нет.</div>
          )}
        </div>

        {user.is_staff && (
          <form className="form-card form" onSubmit={handleCreate}>
            <div className="section-title">Новый пациент</div>

            {[
              ["last_name", "Фамилия"],
              ["first_name", "Имя"],
              ["middle_name", "Отчество"],
              ["birth_date", "Дата рождения", "date"],
              ["phone", "Телефон"],
              ["address", "Адрес"],
              ["passport", "Паспорт"],
              ["card_number", "Номер карты"],
            ].map(([name, label, type = "text"]) => (
              <div className="form-group" key={name}>
                <div className="form-label">{label}</div>
                <input
                  className="input"
                  type={type}
                  value={form[name]}
                  onChange={(event) =>
                    setForm((prev) => ({ ...prev, [name]: event.target.value }))
                  }
                  required={name !== "middle_name"}
                />
              </div>
            ))}

            <div className="form-group">
              <div className="form-label">Пол</div>
              <select
                className="select"
                value={form.gender}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, gender: event.target.value }))
                }
              >
                <option value="F">Женский</option>
                <option value="M">Мужской</option>
              </select>
            </div>

            <button className="button button-primary" type="submit">
              Добавить
            </button>

            {message && <div className="message message-success">{message}</div>}
            {error && <div className="message message-error">{error}</div>}
          </form>
        )}
      </div>
    </div>
  );
}

export default PatientsPage;
