export function el(tag, text = "", className = "") {
  const node = document.createElement(tag);
  node.textContent = text;
  node.className = className;
  return node;
}

export function button(text, action, className = "secondary") {
  const node = el("button", text, className);
  node.type = "button";
  node.addEventListener("click", action);
  return node;
}

export function notice(text) {
  const node = el("p", text, "notice");
  node.setAttribute("role", "status");
  return node;
}

export function table(columns, rows, actions) {
  if (!rows.length) return notice("Записей пока нет");
  const wrap = el("div", "", "table-wrap");
  const grid = el("table");
  const head = grid.createTHead().insertRow();
  for (const [label] of columns) head.append(el("th", label));
  if (actions) head.append(el("th", "Действия"));
  for (const item of rows) {
    const row = grid.createTBody().insertRow();
    for (const [, value] of columns) row.insertCell().textContent = value(item) ?? "–";
    if (actions) row.insertCell().append(actions(item));
  }
  wrap.append(grid);
  return wrap;
}

export function dialog(title, content) {
  const modal = el("dialog");
  const header = el("div", "", "row");
  header.append(el("h2", title), button("Закрыть", () => modal.close()));
  modal.append(header, content);
  modal.addEventListener("close", () => modal.remove());
  document.body.append(modal);
  modal.showModal();
  return modal;
}

export function field(labelText, input) {
  const label = el("label", labelText);
  label.append(input);
  return label;
}
