import "./Navbar.scss";

import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext/AuthContext";

function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  const roleLabel = {
    admin: "админ",
    doctor: "врач",
    patient: "пациент",
    guest: "гость",
  }[user?.role || "guest"];

  return (
    <div className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">
          Clinic
        </Link>

        <div className="navbar-links">
          <Link to="/" className="navbar-link">
            Врачи
          </Link>

          {user?.is_staff && (
            <>
              <Link to="/patients" className="navbar-link">
                Пациенты
              </Link>
              <Link to="/appointments" className="navbar-link">
                Приёмы
              </Link>
              <Link to="/analytics" className="navbar-link">
                Аналитика
              </Link>
            </>
          )}

          {user?.is_doctor && !user?.is_staff && (
            <>
              <Link to="/patients" className="navbar-link">
                Мои пациенты
              </Link>
              <Link to="/appointments" className="navbar-link">
                Мои приёмы
              </Link>
            </>
          )}

          {user?.is_patient && !user?.is_staff && !user?.is_doctor && (
            <>
              <Link to="/appointments" className="navbar-link">
                Мои приёмы
              </Link>
              <Link to="/profile" className="navbar-link">
                Медкарта
              </Link>
            </>
          )}

          {user && !user.is_staff && !user.is_doctor && !user.is_patient && (
            <Link to="/profile" className="navbar-link">
              Оформить медкарту
            </Link>
          )}
        </div>

        <div className="navbar-user">
          {!user ? (
            <>
              <Link to="/login" className="navbar-link">
                Войти
              </Link>
              <Link to="/register" className="button button-primary">
                Регистрация
              </Link>
            </>
          ) : (
            <>
              <div className="navbar-username">
                {user.username} · {roleLabel}
              </div>
              <button className="button button-secondary" onClick={handleLogout}>
                Выйти
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default Navbar;
