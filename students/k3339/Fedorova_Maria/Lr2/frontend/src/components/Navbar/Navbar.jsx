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

  return (
    <div className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">
          Tours
        </Link>

        <div className="navbar-links">
          <Link to="/" className="navbar-link">
            Туры
          </Link>

          {user && (
            <Link to="/reservations" className="navbar-link">
              Мои бронирования
            </Link>
          )}

          {user?.is_staff && (
            <Link to="/admin" className="navbar-link">
              Администрирование
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
              <div className="navbar-username">{user.username}</div>

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
