import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import api from "../../api";
import { useAuth } from "../../context/AuthContext/AuthContext";

import "./ProfilePage.scss";

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

function ProfilePage() {
  const { user, loading: authLoading, loadUser } = useAuth();
  const [card, setCard] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user?.is_patient) {
      return;
    }

    api
      .get("/patients/")
      .then((response) => {
        const list = response.data.results ?? response.data;
        setCard(list[0] || null);
      })
      .catch(() => setError("Не удалось загрузить медкарту"));
  }, [user]);

  async function handleCreate(event) {
    event.preventDefault();
    setMessage("");
    setError("");

    try {
      const response = await api.post("/patients/", form);
      setCard(response.data);
      setMessage("Медкарта создана");
      await loadUser();
    } catch (err) {
      const data = err.response?.data;
      setError(
        typeof data === "object"
          ? Object.values(data).flat().join(" ")
          : "Не удалось создать карту",
      );
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

  if (user.is_staff || user.is_doctor) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">Медицинская карта</div>
        <div className="page-subtitle">
          Пациент оформляет карту один раз, затем видит свои приёмы и оплачивает их.
        </div>
      </div>

      {card ? (
        <div className="card profile-card">
          <div className="card-title">{card.full_name}</div>
          <div className="info-item">
            <div className="info-label">Номер карты</div>
            <div className="info-value">{card.card_number}</div>
          </div>
          <div className="info-item">
            <div className="info-label">Телефон</div>
            <div className="info-value">{card.phone}</div>
          </div>
          <div className="info-item">
            <div className="info-label">Адрес</div>
            <div className="info-value">{card.address}</div>
          </div>
          <div className="info-item">
            <div className="info-label">Дата рождения</div>
            <div className="info-value">{card.birth_date}</div>
          </div>
        </div>
      ) : (
        <form className="form-card form profile-form" onSubmit={handleCreate}>
          <div className="section-title">Оформить карту</div>

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
                required={name !== "middle_name"}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, [name]: event.target.value }))
                }
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
            Сохранить
          </button>

          {message && <div className="message message-success">{message}</div>}
          {error && <div className="message message-error">{error}</div>}
        </form>
      )}
    </div>
  );
}

export default ProfilePage;
