import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import api from "../../api";
import { useAuth } from "../../context/AuthContext/AuthContext";

import "./TourDetailPage.scss";

function TourDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();

  const [tour, setTour] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [text, setText] = useState("");
  const [rating, setRating] = useState(10);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("success");

  async function loadTour() {
    const response = await api.get(`/tours/${id}/`);
    setTour(response.data);
  }

  async function loadReviews() {
    const response = await api.get(`/reviews/?tour=${id}`);
    
    setReviews(response.data.results ?? response.data);
  }

  async function handleReservation() {
    setMessage("");

    try {
      await api.post("/reservations/", {
        tour: Number(id),
      });

      setMessageType("success");
      setMessage("Тур успешно забронирован");
    } catch {
      setMessageType("error");
      setMessage("Не удалось забронировать тур");
    }
  }

  async function handleReviewSubmit(event) {
    event.preventDefault();

    try {
      await api.post("/reviews/", {
        tour: Number(id),
        text,
        rating: Number(rating),
      });

      setText("");
      setRating(10);
      await loadReviews();
    } catch {
      setMessageType("error");
      setMessage("Не удалось добавить отзыв");
    }
  }

  async function handleReviewDelete(reviewId) {
    await api.delete(`/reviews/${reviewId}/`);
    await loadReviews();
  }

  useEffect(() => {
    loadTour();
    loadReviews();
  }, [id]);

  if (!tour) {
    return (
      <div className="page">
        <div className="page-subtitle">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="detail-layout">
        <div className="detail-main">
          <div className="card">
            <div className="tour-country">{tour.country.name}</div>
            <div className="page-title">{tour.name}</div>
            <div className="page-subtitle">{tour.description}</div>

            <div className="detail-info">
              <div className="info-item">
                <div className="info-label">Агентство</div>
                <div className="info-value">{tour.agency.name}</div>
              </div>

              <div className="info-item">
                <div className="info-label">Стоимость</div>
                <div className="info-value">{tour.price} ₽</div>
              </div>

              <div className="info-item">
                <div className="info-label">Начало</div>
                <div className="info-value">{tour.start_date}</div>
              </div>

              <div className="info-item">
                <div className="info-label">Окончание</div>
                <div className="info-value">{tour.end_date}</div>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="section-title">Условия оплаты</div>
            <div className="card-description">{tour.payment_terms}</div>
          </div>

          <div className="card">
            <div className="section-title">Отзывы</div>

            {reviews.length === 0 ? (
              <div className="card-description">Отзывов пока нет.</div>
            ) : (
              <div className="reviews">
                {reviews.map((review) => (
                  <div className="review" key={review.id}>
                    <div className="review-header">
                      <div className="review-author">
                        {review.user.username}
                      </div>
                      <div className="review-rating">
                        {review.rating}/10
                      </div>
                    </div>

                    <div className="review-text">{review.text}</div>

                    {review.start_date && review.end_date && (
                      <div className="review-date">
                        Даты тура: {review.start_date} — {review.end_date}
                      </div>
                    )}

                    <div className="review-date">
                      {new Date(review.created_at).toLocaleString()}
                    </div>

                    {user?.id === review.user.id && (
                      <button
                        className="button button-danger"
                        onClick={() => handleReviewDelete(review.id)}
                        style={{ marginTop: 12 }}
                      >
                        Удалить отзыв
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}

            {user && (
              <>
                <div className="section-title" style={{ marginTop: 28 }}>
                  Оставить отзыв
                </div>

                <form className="form" onSubmit={handleReviewSubmit}>
                  <div className="form-group">
                    <div className="form-label">Текст отзыва</div>
                    <div className="textarea-scroll">
                      <textarea
                        className="textarea"
                        value={text}
                        onChange={(event) => setText(event.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <div className="form-label">Рейтинг</div>
                    <select
                      className="select"
                      value={rating}
                      onChange={(event) => setRating(event.target.value)}
                    >
                      {Array.from({ length: 10 }, (_, index) => index + 1).map(
                        (value) => (
                          <option key={value} value={value}>
                            {value}
                          </option>
                        ),
                      )}
                    </select>
                  </div>

                  <button className="button button-primary" type="submit">
                    Отправить отзыв
                  </button>
                </form>
              </>
            )}
          </div>
        </div>

        <div className="form-card">
          <div className="section-title">Бронирование</div>

          {user ? (
            <>
              <div className="card-description">
                Забронируйте тур. После этого заявка будет ожидать
                подтверждения администратора.
              </div>
              <br />
              <button
                className="button button-primary"
                onClick={handleReservation}
              >
                Забронировать
              </button>
            </>
          ) : (
            <div className="card-description">
              Для бронирования необходимо войти в аккаунт.
            </div>
          )}

          {message && (
            <div
              className={`message ${
                messageType === "error" ? "message-error" : "message-success"
              }`}
            >
              {message}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default TourDetailPage;
