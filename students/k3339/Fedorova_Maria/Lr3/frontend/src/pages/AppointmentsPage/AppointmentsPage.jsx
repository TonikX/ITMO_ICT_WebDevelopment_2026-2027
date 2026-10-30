import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import AppointmentCard from "../../components/AppointmentCard/AppointmentCard";
import api from "../../api";
import { useAuth } from "../../context/AuthContext/AuthContext";

import "./AppointmentsPage.scss";

function AppointmentsPage() {
  const { user, loading: authLoading } = useAuth();
  const [appointments, setAppointments] = useState([]);
  const [patients, setPatients] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [services, setServices] = useState([]);
  const [cabinets, setCabinets] = useState([]);
  const [form, setForm] = useState({
    patient: "",
    doctor: "",
    cabinet: "",
    service: "",
    visited_at: "",
    diagnosis: "",
    condition: "",
    recommendations: "",
  });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const canManage = user?.is_staff || user?.is_doctor;
  const canPay = Boolean(user?.is_patient && !user?.is_staff && !user?.is_doctor);
  const canBook = user?.is_patient && !user?.is_staff && !user?.is_doctor;

  async function loadAll() {
    const requests = [api.get("/appointments/"), api.get("/services/")];

    if (canManage || canBook) {
      requests.push(api.get("/doctors/"));
    }
    if (canManage) {
      requests.push(api.get("/patients/"), api.get("/cabinets/"));
    }

    const responses = await Promise.all(requests);
    setAppointments(responses[0].data.results ?? responses[0].data);
    setServices(responses[1].data.results ?? responses[1].data);

    let index = 2;
    if (canManage || canBook) {
      setDoctors(responses[index].data.results ?? responses[index].data);
      index += 1;
    }
    if (canManage) {
      setPatients(responses[index].data.results ?? responses[index].data);
      setCabinets(responses[index + 1].data.results ?? responses[index + 1].data);
    }
  }

  useEffect(() => {
    if (user && (user.is_staff || user.is_doctor || user.is_patient)) {
      loadAll().catch(() => setError("Не удалось загрузить данные"));
    }
  }, [user]);

  async function handleCreate(event) {
    event.preventDefault();
    setError("");
    setMessage("");

    try {
      if (canBook) {
        await api.post("/appointments/", {
          doctor: Number(form.doctor),
          service: Number(form.service),
          visited_at: form.visited_at,
        });
        setMessage("Вы записаны на приём");
      } else {
        const payload = {
          patient: Number(form.patient),
          service: Number(form.service),
          cabinet: form.cabinet ? Number(form.cabinet) : null,
          visited_at: form.visited_at,
          diagnosis: form.diagnosis,
          condition: form.condition,
          recommendations: form.recommendations,
        };

        if (user.is_staff) {
          payload.doctor = Number(form.doctor);
        } else {
          payload.doctor = user.doctor_id;
        }

        await api.post("/appointments/", payload);
        setMessage("Приём создан");
      }

      setForm({
        patient: "",
        doctor: "",
        cabinet: "",
        service: "",
        visited_at: "",
        diagnosis: "",
        condition: "",
        recommendations: "",
      });
      await loadAll();
    } catch {
      setError(canBook ? "Не удалось записаться" : "Не удалось создать приём");
    }
  }

  async function handlePay(id) {
    await api.patch(`/appointments/${id}/pay/`);
    await loadAll();
  }

  async function handleDiagnose(id, payload) {
    await api.patch(`/appointments/${id}/`, payload);
    setMessage("Диагноз сохранён");
    await loadAll();
  }

  const canDiagnose = Boolean(user?.is_doctor || user?.is_staff);

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

  if (!user.is_staff && !user.is_doctor && !user.is_patient) {
    return <Navigate to="/profile" replace />;
  }

  const title = user.is_staff
    ? "Приёмы"
    : user.is_doctor
      ? "Мои приёмы"
      : "Мои приёмы и оплата";

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">{title}</div>
        <div className="page-subtitle">
          {user.is_patient
            ? "Здесь ваши визиты. Неоплаченные можно оплатить."
            : "Фиксация приёма: диагноз, состояние, услуга из прайса."}
        </div>
      </div>

      <div className="appointments-layout">
        <div className="appointments-list">
          {appointments.map((item) => (
            <AppointmentCard
              key={item.id}
              appointment={item}
              onPay={canPay ? handlePay : null}
              onDiagnose={canDiagnose ? handleDiagnose : null}
            />
          ))}
          {appointments.length === 0 && (
            <div className="page-subtitle">Приёмов пока нет.</div>
          )}
        </div>

        {(canManage || canBook) && (
          <form className="form-card form" onSubmit={handleCreate}>
            <div className="section-title">
              {canBook ? "Записаться на приём" : "Новый приём"}
            </div>

            {canManage && (
              <div className="form-group">
                <div className="form-label">Пациент</div>
                <select
                  className="select"
                  value={form.patient}
                  onChange={(event) =>
                    setForm((prev) => ({ ...prev, patient: event.target.value }))
                  }
                  required
                >
                  <option value="">Выберите</option>
                  {patients.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.full_name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {(user.is_staff || canBook) && (
              <div className="form-group">
                <div className="form-label">Врач</div>
                <select
                  className="select"
                  value={form.doctor}
                  onChange={(event) =>
                    setForm((prev) => ({ ...prev, doctor: event.target.value }))
                  }
                  required
                >
                  <option value="">Выберите</option>
                  {doctors.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.full_name} ({item.specialty})
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="form-group">
              <div className="form-label">Услуга</div>
              <select
                className="select"
                value={form.service}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, service: event.target.value }))
                }
                required
              >
                <option value="">Выберите</option>
                {services.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name} — {item.price} ₽
                  </option>
                ))}
              </select>
            </div>

            {canManage && (
              <div className="form-group">
                <div className="form-label">Кабинет</div>
                <select
                  className="select"
                  value={form.cabinet}
                  onChange={(event) =>
                    setForm((prev) => ({ ...prev, cabinet: event.target.value }))
                  }
                >
                  <option value="">Не указан</option>
                  {cabinets.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.number}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="form-group">
              <div className="form-label">Дата и время</div>
              <input
                className="input"
                type="datetime-local"
                value={form.visited_at}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, visited_at: event.target.value }))
                }
                required
              />
            </div>

            {canManage && (
              <>
                <div className="form-group">
                  <div className="form-label">Диагноз</div>
                  <input
                    className="input"
                    value={form.diagnosis}
                    onChange={(event) =>
                      setForm((prev) => ({ ...prev, diagnosis: event.target.value }))
                    }
                    required
                  />
                </div>

                <div className="form-group">
                  <div className="form-label">Состояние</div>
                  <div className="textarea-scroll">
                    <textarea
                      className="textarea"
                      value={form.condition}
                      onChange={(event) =>
                        setForm((prev) => ({
                          ...prev,
                          condition: event.target.value,
                        }))
                      }
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <div className="form-label">Рекомендации</div>
                  <div className="textarea-scroll">
                    <textarea
                      className="textarea"
                      value={form.recommendations}
                      onChange={(event) =>
                        setForm((prev) => ({
                          ...prev,
                          recommendations: event.target.value,
                        }))
                      }
                    />
                  </div>
                </div>
              </>
            )}

            <button className="button button-primary" type="submit">
              {canBook ? "Записаться" : "Создать приём"}
            </button>

            {message && <div className="message message-success">{message}</div>}
            {error && <div className="message message-error">{error}</div>}
          </form>
        )}
      </div>

      {error && !canManage && (
        <div className="message message-error">{error}</div>
      )}
    </div>
  );
}

export default AppointmentsPage;
