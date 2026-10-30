import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import api from "../../api";
import { useAuth } from "../../context/AuthContext/AuthContext";

import "./AnalyticsPage.scss";

function AnalyticsPage() {
  const { user, loading: authLoading } = useAuth();
  const [doctors, setDoctors] = useState([]);
  const [doctorId, setDoctorId] = useState("");
  const [weekday, setWeekday] = useState("0");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const [doctorPatients, setDoctorPatients] = useState([]);
  const [entPatients, setEntPatients] = useState([]);
  const [byWeekday, setByWeekday] = useState([]);
  const [byDate, setByDate] = useState([]);
  const [costs, setCosts] = useState({ by_day: [], by_doctor: [] });
  const [paidPatients, setPaidPatients] = useState([]);
  const [report, setReport] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user) {
      return;
    }

    async function bootstrap() {
      const doctorsRes = await api.get("/doctors/");
      const list = doctorsRes.data.results ?? doctorsRes.data;
      setDoctors(list);
      if (list[0]) {
        setDoctorId(String(list[0].id));
      }
    }

    bootstrap().catch(() => setError("Не удалось загрузить врачей"));
  }, [user]);

  async function loadAnalytics() {
    setError("");

    try {
      const [
        doctorPatientsRes,
        entRes,
        weekdayRes,
        datesRes,
        costsRes,
        paidRes,
      ] = await Promise.all([
        api.get("/analytics/doctor-patients/", {
          params: { doctor: doctorId || undefined },
        }),
        api.get("/analytics/ent-patients/"),
        api.get("/analytics/doctors-by-weekday/", {
          params: { weekday },
        }),
        api.get("/analytics/appointments-by-date/"),
        api.get("/analytics/costs/"),
        api.get("/analytics/paid-patients/"),
      ]);

      setDoctorPatients(doctorPatientsRes.data);
      setEntPatients(entRes.data);
      setByWeekday(weekdayRes.data);
      setByDate(datesRes.data);
      setCosts(costsRes.data);
      setPaidPatients(paidRes.data);

      if (user.is_staff) {
        const reportRes = await api.get("/analytics/doctors-report/", {
          params: {
            from: dateFrom || undefined,
            to: dateTo || undefined,
          },
        });
        setReport(reportRes.data);
      }
    } catch {
      setError("Не удалось загрузить аналитику");
    }
  }

  useEffect(() => {
    if (user && doctorId) {
      loadAnalytics();
    }
  }, [user, doctorId, weekday]);

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

  if (!user.is_staff) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">Аналитика</div>
        <div className="page-subtitle">
          Запросы и отчёт по работе врачей из варианта задания.
        </div>
      </div>

      <div className="analytics-controls card">
        <div className="form-group">
          <div className="form-label">Врач</div>
          <select
            className="select"
            value={doctorId}
            onChange={(event) => setDoctorId(event.target.value)}
          >
            {doctors.map((doctor) => (
              <option key={doctor.id} value={doctor.id}>
                {doctor.full_name}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <div className="form-label">День недели</div>
          <select
            className="select"
            value={weekday}
            onChange={(event) => setWeekday(event.target.value)}
          >
            <option value="0">Понедельник</option>
            <option value="1">Вторник</option>
            <option value="2">Среда</option>
            <option value="3">Четверг</option>
            <option value="4">Пятница</option>
            <option value="5">Суббота</option>
            <option value="6">Воскресенье</option>
          </select>
        </div>

        {user.is_staff && (
          <>
            <div className="form-group">
              <div className="form-label">Отчёт с</div>
              <input
                className="input"
                type="date"
                value={dateFrom}
                onChange={(event) => setDateFrom(event.target.value)}
              />
            </div>
            <div className="form-group">
              <div className="form-label">Отчёт по</div>
              <input
                className="input"
                type="date"
                value={dateTo}
                onChange={(event) => setDateTo(event.target.value)}
              />
            </div>
          </>
        )}

        <button className="button button-primary" type="button" onClick={loadAnalytics}>
          Обновить
        </button>
      </div>

      {error && <div className="message message-error">{error}</div>}

      <div className="analytics-grid">
        <section className="card">
          <div className="section-title">Пациенты выбранного врача</div>
          {doctorPatients.map((item, index) => (
            <div className="analytics-row" key={`${item.patient}-${index}`}>
              <strong>{item.patient}</strong>
              <span>{new Date(item.visited_at).toLocaleString("ru-RU")}</span>
              <span>{item.cost} ₽</span>
            </div>
          ))}
        </section>

        <section className="card">
          <div className="section-title">ЛОР, год рождения &gt; 1987</div>
          {entPatients.map((item) => (
            <div className="analytics-row" key={item.phone}>
              <strong>{item.full_name}</strong>
              <span>{item.phone}</span>
            </div>
          ))}
        </section>

        <section className="card">
          <div className="section-title">Врачи в выбранный день</div>
          {byWeekday.map((item) => (
            <div className="analytics-row" key={item.id}>
              <strong>{item.full_name}</strong>
              <span>{item.specialty}</span>
            </div>
          ))}
        </section>

        <section className="card">
          <div className="section-title">Приёмы по датам</div>
          {byDate.map((item) => (
            <div className="analytics-row" key={item.day}>
              <strong>{item.day}</strong>
              <span>{item.total}</span>
            </div>
          ))}
        </section>

        <section className="card">
          <div className="section-title">Суммы по дням</div>
          {costs.by_day?.map((item) => (
            <div className="analytics-row" key={item.day}>
              <strong>{item.day}</strong>
              <span>{item.total_cost} ₽</span>
            </div>
          ))}
        </section>

        <section className="card">
          <div className="section-title">Суммы по врачам</div>
          {costs.by_doctor?.map((item) => (
            <div className="analytics-row" key={item.doctor_id}>
              <strong>
                {item.doctor__last_name} {item.doctor__first_name}
              </strong>
              <span>{item.total_cost} ₽</span>
            </div>
          ))}
        </section>

        <section className="card">
          <div className="section-title">Оплатившие пациенты</div>
          {paidPatients.map((item) => (
            <div className="analytics-row" key={item.id}>
              <strong>{item.full_name}</strong>
              <span>{item.phone}</span>
            </div>
          ))}
        </section>

        {user.is_staff && (
          <section className="card analytics-report">
            <div className="section-title">Отчёт по врачам</div>
            {report.map((item) => (
              <div className="report-block" key={item.doctor}>
                <div className="card-title">
                  {item.doctor} · доход {item.total_income} ₽
                </div>
                {item.patients.map((visit, index) => (
                  <div className="analytics-row" key={`${item.doctor}-${index}`}>
                    <span>{visit.patient}</span>
                    <span>{visit.diagnosis}</span>
                    <span>{visit.cost} ₽</span>
                  </div>
                ))}
              </div>
            ))}
          </section>
        )}
      </div>
    </div>
  );
}

export default AnalyticsPage;
