import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../../api";

import "./DoctorsPage.scss";

function DoctorsPage() {
  const [doctors, setDoctors] = useState([]);
  const [search, setSearch] = useState("");
  const [specialty, setSpecialty] = useState("");
  const [ordering, setOrdering] = useState("last_name");
  const [page, setPage] = useState(1);
  const [count, setCount] = useState(0);
  const [next, setNext] = useState(null);
  const [previous, setPrevious] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadDoctors(pageNumber = page) {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/doctors/", {
        params: {
          page: pageNumber,
          search: search.trim() || undefined,
          specialty: specialty.trim() || undefined,
          ordering,
        },
      });

      setDoctors(response.data.results);
      setCount(response.data.count);
      setNext(response.data.next);
      setPrevious(response.data.previous);
    } catch {
      setError("Не удалось загрузить врачей");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDoctors();
  }, [page, ordering]);

  function handleSearch(event) {
    event.preventDefault();
    if (page !== 1) {
      setPage(1);
      return;
    }
    loadDoctors(1);
  }

  function handleReset() {
    setSearch("");
    setSpecialty("");
    setOrdering("last_name");
    if (page !== 1) {
      setPage(1);
      return;
    }
    setTimeout(() => loadDoctors(1), 0);
  }

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">Врачи клиники</div>
        <div className="page-subtitle">
          Специалисты, график работы и коммерческий приём пациентов.
        </div>
      </div>

      <form className="filters" onSubmit={handleSearch}>
        <div className="form-group">
          <div className="form-label">Поиск</div>
          <input
            className="input"
            type="text"
            value={search}
            placeholder="ФИО или специальность"
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>

        <div className="form-group">
          <div className="form-label">Специальность</div>
          <input
            className="input"
            type="text"
            value={specialty}
            placeholder="Терапевт"
            onChange={(event) => setSpecialty(event.target.value)}
          />
        </div>

        <div className="form-group">
          <div className="form-label">Сортировка</div>
          <select
            className="select"
            value={ordering}
            onChange={(event) => setOrdering(event.target.value)}
          >
            <option value="last_name">По фамилии</option>
            <option value="specialty">По специальности</option>
            <option value="work_start">По дате найма</option>
          </select>
        </div>

        <div className="filters-actions">
          <button className="button button-primary" type="submit">
            Найти
          </button>
          <button
            className="button button-secondary"
            type="button"
            onClick={handleReset}
          >
            Сброс
          </button>
        </div>
      </form>

      {loading && <div className="page-subtitle">Загрузка...</div>}
      {error && <div className="message message-error">{error}</div>}

      {!loading && !error && (
        <>
          <div className="doctors-grid">
            {doctors.map((doctor) => (
              <div className="card doctor-card" key={doctor.id}>
                <div className="doctor-specialty">{doctor.specialty}</div>
                <div className="card-title">{doctor.full_name}</div>
                <div className="card-description">{doctor.education}</div>
                <div className="doctor-meta">
                  <span>С {doctor.work_start}</span>
                  <span>Договор {doctor.contract_number}</span>
                </div>
                <div className="doctor-card-footer">
                  <Link
                    className="button button-secondary"
                    to={`/doctors/${doctor.id}`}
                  >
                    Подробнее
                  </Link>
                  <Link
                    className="button button-primary"
                    to={`/doctors/${doctor.id}`}
                  >
                    Записаться
                  </Link>
                </div>
              </div>
            ))}
          </div>

          {doctors.length === 0 && (
            <div className="page-subtitle">Врачи не найдены.</div>
          )}

          <div className="pagination">
            <button
              className="pagination-arrow"
              disabled={!previous}
              onClick={() => setPage((value) => value - 1)}
            >
              ‹
            </button>
            <div className="pagination-label">
              {page} / {Math.max(1, Math.ceil(count / 8))}
            </div>
            <button
              className="pagination-arrow"
              disabled={!next}
              onClick={() => setPage((value) => value + 1)}
            >
              ›
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default DoctorsPage;
