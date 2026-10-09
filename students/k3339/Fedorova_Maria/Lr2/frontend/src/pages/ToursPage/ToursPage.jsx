import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../../api";

import "./ToursPage.scss";

function ToursPage() {
  const [tours, setTours] = useState([]);
  const [search, setSearch] = useState("");
  const [country, setCountry] = useState("");
  const [agency, setAgency] = useState("");
  const [ordering, setOrdering] = useState("start_date");

  const [page, setPage] = useState(1);
  const [count, setCount] = useState(0);
  const [next, setNext] = useState(null);
  const [previous, setPrevious] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadTours(pageNumber = page) {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/tours/", {
        params: {
          page: pageNumber,
          search: search.trim() || undefined,
          country: country.trim() || undefined,
          agency: agency.trim() || undefined,
          ordering,
        },
      });

      setTours(response.data.results);
      setCount(response.data.count);
      setNext(response.data.next);
      setPrevious(response.data.previous);
    } catch {
      setError("Не удалось загрузить туры");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadTours();
  }, [page, ordering]);

  function handleSearch(event) {
    event.preventDefault();

    if (page !== 1) {
      setPage(1);
      return;
    }

    loadTours(1);
  }

  function handleReset() {
    setSearch("");
    setCountry("");
    setAgency("");
    setOrdering("start_date");

    if (page !== 1) {
      setPage(1);
      return;
    }

    setTimeout(() => loadTours(1), 0);
  }

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">Туры</div>
        <div className="page-subtitle">
          Выберите направление и подходящий период путешествия.
        </div>
      </div>

      <form className="filters" onSubmit={handleSearch}>
        <div className="form-group">
          <div className="form-label">Поиск</div>
          <input
            className="input"
            type="text"
            value={search}
            placeholder="Название, страна, агентство"
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>

        <div className="form-group">
          <div className="form-label">Страна</div>
          <input
            className="input"
            type="text"
            value={country}
            placeholder="Fra, Italy..."
            onChange={(event) => setCountry(event.target.value)}
          />
        </div>

        <div className="form-group">
          <div className="form-label">Агентство</div>
          <input
            className="input"
            type="text"
            value={agency}
            placeholder="Sun, Travel..."
            onChange={(event) => setAgency(event.target.value)}
          />
        </div>

        <div className="form-group">
          <div className="form-label">Сортировка</div>
          <select
            className="select"
            value={ordering}
            onChange={(event) => {
              setOrdering(event.target.value);
              setPage(1);
            }}
          >
            <option value="start_date">По дате начала</option>
            <option value="price">Сначала дешевле</option>
            <option value="-price">Сначала дороже</option>
            <option value="name">По названию</option>
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
            Сбросить
          </button>
        </div>
      </form>

      <div className="page-subtitle">Найдено туров: {count}</div>

      {loading && <div className="page-subtitle">Загрузка...</div>}
      {error && <div className="message message-error">{error}</div>}
      {!loading && tours.length === 0 && (
        <div className="page-subtitle">Туры не найдены.</div>
      )}

      {!loading && (
        <div className="tours-grid">
          {tours.map((tour) => (
            <div className="card tour-card" key={tour.id}>
              <div>
                <div className="tour-card-top">
                  <div>
                    <div className="tour-country">{tour.country.name}</div>
                    <div className="card-title">{tour.name}</div>
                    <div className="card-description">{tour.description}</div>
                  </div>
                  <div className="tour-price">{tour.price} ₽</div>
                </div>

                <div className="tour-meta">
                  <div>{tour.agency.name}</div>
                  <div>{tour.start_date}</div>
                  <div>{tour.end_date}</div>
                </div>
              </div>

              <div className="tour-card-footer">
                <Link
                  className="button button-primary"
                  to={`/tours/${tour.id}`}
                >
                  Подробнее
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="pagination">
        <button
          className="pagination-arrow"
          type="button"
          aria-label="Предыдущая страница"
          disabled={!previous}
          onClick={() => setPage(page - 1)}
        >
          ‹
        </button>

        <div className="pagination-label">{page}</div>

        <button
          className="pagination-arrow"
          type="button"
          aria-label="Следующая страница"
          disabled={!next}
          onClick={() => setPage(page + 1)}
        >
          ›
        </button>
      </div>
    </div>
  );
}

export default ToursPage;
