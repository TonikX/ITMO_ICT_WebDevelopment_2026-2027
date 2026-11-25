import { api, getToken, setToken } from "./api.js";
import { button, dialog, el, field, notice, table } from "./components.js";
import { editRecord, leaseAction } from "./editor.js";
import { neighborsTable, reports } from "./reports.js";
import { columns, displayName, labels, names, relations } from "./resources.js";

const main = document.querySelector("#main");
const nav = document.querySelector("#nav");
const account = document.querySelector("#account");
const sections = {animals: "Реестр", leases: "Аренда", directories: "Справочники", reports: "Отчёты"};

function loginView(register = false) {
  const panel = el("section", "", "panel login");
  const form = el("form");
  const username = el("input");
  username.required = true;
  username.autocomplete = "username";
  const password = el("input");
  password.type = "password";
  password.required = true;
  password.autocomplete = register ? "new-password" : "current-password";
  const message = notice("");
  const submit = el("button", register ? "Создать аккаунт" : "Войти", "primary");
  form.append(field("Имя пользователя", username), field("Пароль", password), message, submit);
  form.addEventListener("submit", async event => {
    event.preventDefault();
    submit.disabled = true;
    const data = {username: username.value, password: password.value};
    try {
      if (register) await api("auth/users/", "POST", data);
      const token = await api("auth/token/login/", "POST", data);
      setToken(token.auth_token);
      await initialize();
    } catch (error) {
      message.textContent = error.message;
    } finally {
      submit.disabled = false;
    }
  });
  panel.append(el("h1", register ? "Регистрация" : "Вход в реестр"), form);
  panel.append(button(register ? "Уже есть аккаунт" : "Создать аккаунт", () => loginView(!register), "quiet"));
  main.replaceChildren(panel);
}

function displayValue(name, value, lookups, metadata) {
  if (value == null || value === "") return null;
  if (relations[name]) {
    const target = lookups[name]?.find(item => item.id === value);
    return target ? displayName(target) : "#" + value;
  }
  if (typeof value === "boolean") return value ? "Да" : "Нет";
  if (name.endsWith("_at")) return new Date(value).toLocaleString("ru-RU");
  return metadata[name]?.choices?.find(choice => choice.value === value)?.display_name || value;
}

async function displayResource(resource, panel) {
  const [rows, options] = await Promise.all([api(resource + "/"), api(resource + "/", "OPTIONS")]);
  const metadata = options.actions.POST;
  const keys = columns[resource] || Object.entries(metadata)
    .filter(([name, spec]) => name !== "id" && !spec.read_only)
    .map(([name]) => name).slice(0, 6);
  const relationFields = Object.keys(metadata).filter(name => relations[name]);
  const lookups = Object.fromEntries(await Promise.all(relationFields.map(async name => [
    name, await api(relations[name] + "/"),
  ])));
  const reload = () => displayResource(resource, panel);
  const toolbar = el("div", "", "row toolbar");
  const search = el("input");
  search.type = "search";
  search.placeholder = "Поиск по таблице";
  search.setAttribute("aria-label", "Поиск по таблице");
  const list = el("div");
  const message = notice("");
  toolbar.append(search, button("Добавить", safely(() => editRecord(resource, metadata, null, reload)), "primary"));

  function safely(action) {
    return async () => {
      message.textContent = "";
      try {
        await action();
      } catch (error) {
        message.textContent = error.message;
      }
    };
  }

  const valueOf = (name, row) => displayValue(name, row[name], lookups, metadata);

  function details(row) {
    const details = el("div");
    const fields = el("dl", "", "details");
    for (const [name, value] of Object.entries(row)) {
      if (name === "id" || Array.isArray(value) || ["species_name", "enclosure_number"].includes(name)) continue;
      fields.append(el("dt", labels[name] || name), el("dd", valueOf(name, row) ?? "–"));
    }
    details.append(fields);
    if (row.employees?.length) {
      details.append(el("h3", "Ответственные сотрудники"), table([
        ["Сотрудник", displayName], ["Роль", employee => employee.role === "vet" ? "Ветеринар" : "Смотритель"],
      ], row.employees));
    }
    dialog(displayName(row), details);
  }

  function rowActions(row) {
    const actions = el("div", "", "actions");
    actions.append(button("Открыть", () => details(row), "quiet"));
    if (resource !== "leases" || !row.transferred_at) {
      actions.append(button("Изменить", safely(() => editRecord(resource, metadata, row, reload)), "quiet"));
      actions.append(button("Удалить", safely(async () => {
        if (confirm("Удалить эту запись?")) {
          await api(resource + "/" + row.id + "/", "DELETE");
          await reload();
        }
      }), "quiet danger"));
    }
    if (resource === "animals") actions.append(button("Соседи", safely(async () => {
      const neighbors = await api("animals/" + row.id + "/building-neighbors/");
      dialog("Животные в том же здании", neighborsTable(neighbors));
    }), "quiet"));
    if (resource === "leases" && !row.returned_at) {
      actions.append(button(row.transferred_at ? "Вернуть" : "Передать", safely(() => (
        leaseAction(row, row.transferred_at ? "return" : "transfer", reload)
      )), "quiet"));
    }
    return actions;
  }

  function draw() {
    const query = search.value.trim().toLocaleLowerCase("ru");
    const visible = rows.filter(row => keys.some(name => (
      String(valueOf(name, row) ?? "").toLocaleLowerCase("ru").includes(query)
    )));
    list.replaceChildren(table(keys.map(name => [labels[name] || name, row => valueOf(name, row)]), visible, rowActions));
  }

  search.addEventListener("input", draw);
  panel.replaceChildren(toolbar, message, list);
  draw();
}

async function showPage() {
  if (!getToken()) return;
  const hash = location.hash.slice(1);
  const selected = Object.hasOwn(sections, hash) ? hash : "animals";
  const panel = el("section", "", selected === "reports" ? "" : "panel");
  main.replaceChildren(el("h1", sections[selected]), panel);
  panel.append(notice("Загрузка…"));
  for (const link of nav.children) {
    if (link.hash === "#" + selected) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  }
  try {
    if (selected === "reports") panel.replaceChildren(await reports());
    else if (selected === "directories") {
      const select = el("select");
      const content = el("div");
      for (const [key, name] of Object.entries(names)) {
        if (key !== "animals" && key !== "leases") select.append(new Option(name, key));
      }
      async function refresh() {
        const area = el("div");
        content.replaceChildren(area);
        try {
          await displayResource(select.value, area);
        } catch (error) {
          area.replaceChildren(notice(error.message));
        }
      }
      select.addEventListener("change", refresh);
      panel.replaceChildren(field("Справочник", select), content);
      await refresh();
    } else await displayResource(selected, panel);
  } catch (error) {
    panel.replaceChildren(notice(error.message));
  }
}

async function initialize() {
  nav.replaceChildren();
  account.replaceChildren();
  if (getToken()) {
    try {
      const user = await api("auth/users/me/");
      for (const [route, title] of Object.entries(sections)) {
        const link = el("a", title);
        link.href = "#" + route;
        nav.append(link);
      }
      account.append(el("span", user.username), button("Выйти", async () => {
        try {
          await api("auth/token/logout/", "POST");
        } finally {
          setToken(null);
          await initialize();
        }
      }, "quiet"));
      await showPage();
      return;
    } catch {
      setToken(null);
    }
  }
  loginView();
}

window.addEventListener("hashchange", showPage);
initialize();
