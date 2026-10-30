import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext/AuthContext";

import "./LoginPage.scss";

function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({
    username: "",
    password: "",
  });

  const navigate = useNavigate();
  const { login } = useAuth();

  async function handleSubmit(event) {
    event.preventDefault();

    const nextErrors = {
      username: username.trim() ? "" : "Обязательное поле",
      password: password ? "" : "Обязательное поле",
    };

    setErrors(nextErrors);

    if (nextErrors.username || nextErrors.password) {
      return;
    }

    try {
      await login(username, password);
      navigate("/");
    } catch {
      setErrors({
        username: "Неверный логин или пароль",
        password: "",
      });
    }
  }

  return (
    <div className="auth-layout">
      <div className="form-card auth-card">
        <div className="page-title">Вход</div>

        <form className="form auth-form" onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <div className="form-label">Логин</div>
            <input
              className="input"
              type="text"
              value={username}
              onChange={(event) => {
                setUsername(event.target.value);
                setErrors((prev) => ({ ...prev, username: "" }));
              }}
            />
            <div className="field-error">{errors.username}</div>
          </div>

          <div className="form-group">
            <div className="form-label">Пароль</div>
            <input
              className="input"
              type="password"
              value={password}
              onChange={(event) => {
                setPassword(event.target.value);
                setErrors((prev) => ({ ...prev, password: "" }));
              }}
            />
            <div className="field-error">{errors.password}</div>
          </div>

          <button className="button button-primary" type="submit">
            Войти
          </button>
        </form>
      </div>
    </div>
  );
}

export default LoginPage;
