import { useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../../api";

import "./RegisterPage.scss";

function RegisterPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({
    username: "",
    email: "",
    password: "",
  });

  const navigate = useNavigate();

  async function handleSubmit(event) {
    event.preventDefault();

    const nextErrors = {
      username: username.trim() ? "" : "Обязательное поле",
      email: email.trim() ? "" : "Обязательное поле",
      password: password ? "" : "Обязательное поле",
    };

    setErrors(nextErrors);

    if (nextErrors.username || nextErrors.email || nextErrors.password) {
      return;
    }

    try {
      await api.post("/register/", {
        username,
        email,
        password,
      });

      navigate("/login");
    } catch {
      setErrors({
        username: "Не удалось зарегистрироваться",
        email: "",
        password: "",
      });
    }
  }

  return (
    <div className="auth-layout">
      <div className="form-card auth-card">
        <div className="page-title">Регистрация</div>

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
            <div className="form-label">Email</div>
            <input
              className="input"
              type="email"
              value={email}
              onChange={(event) => {
                setEmail(event.target.value);
                setErrors((prev) => ({ ...prev, email: "" }));
              }}
            />
            <div className="field-error">{errors.email}</div>
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
            Зарегистрироваться
          </button>
        </form>
      </div>
    </div>
  );
}

export default RegisterPage;
