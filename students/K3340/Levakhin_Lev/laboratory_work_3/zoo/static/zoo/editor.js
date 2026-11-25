import { api } from "./api.js";
import { button, dialog, el, field, notice } from "./components.js";
import { displayName, labels, relations } from "./resources.js";

export function recordSelect(records, value, required) {
  const select = el("select");
  select.append(new Option(required ? "Выберите значение" : "Без значения", ""));
  for (const record of records) select.append(new Option(displayName(record), record.id));
  select.value = value ?? "";
  return select;
}

const textAreas = new Set(["care_notes", "description", "contents", "equipment"]);

function localDateTime(value) {
  const date = new Date(value);
  return new Date(date - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}

export async function editRecord(resource, metadata, row, reload) {
  const form = el("form", "", "record-form");
  const fields = el("div", "", "fields");
  const inputs = await Promise.all(Object.entries(metadata).filter(([, spec]) => !spec.read_only).map(
    async ([name, spec]) => {
      const value = row?.[name];
      let input;
      if (relations[name]) {
        input = recordSelect(await api(relations[name] + "/"), value, spec.required);
      } else if (spec.choices) {
        input = el("select");
        input.append(new Option("Выберите значение", ""));
        for (const choice of spec.choices) input.append(new Option(choice.display_name, choice.value));
        input.value = value ?? "";
      } else if (textAreas.has(name)) {
        input = el("textarea");
        input.value = value ?? "";
      } else {
        input = el("input");
        input.type = {date: "date", datetime: "datetime-local", email: "email", boolean: "checkbox"}[spec.type] || (
          ["integer", "decimal", "float"].includes(spec.type) ? "number" : "text"
        );
        if (input.type === "checkbox") input.checked = value ?? false;
        else input.value = value && input.type === "datetime-local" ? localDateTime(value) : value ?? "";
        if (input.type === "number" && spec.type !== "integer") input.step = "any";
      }
      input.required = spec.required && input.type !== "checkbox";
      return [name, input, spec];
    },
  ));
  for (const [name, input] of inputs) fields.append(field(labels[name] || name, input));
  const message = notice("");
  const submit = el("button", "Сохранить", "primary");
  form.append(fields, message, submit);
  const modal = dialog(row ? "Изменить запись" : "Добавить запись", form);
  form.addEventListener("submit", async event => {
    event.preventDefault();
    submit.disabled = true;
    try {
      const data = Object.fromEntries(inputs.map(([name, input, spec]) => {
        if (input.type === "checkbox") return [name, input.checked];
        if (input.type === "datetime-local" && input.value) return [name, new Date(input.value).toISOString()];
        if (!input.value && (relations[name] || ["date", "datetime", "decimal"].includes(spec.type))) return [name, null];
        return [name, input.value];
      }));
      await api(resource + "/" + (row ? row.id + "/" : ""), row ? "PATCH" : "POST", data);
      modal.close();
      await reload();
    } catch (error) {
      message.textContent = error.message;
    } finally {
      submit.disabled = false;
    }
  });
}

export async function leaseAction(row, action, reload) {
  const [zoos, enclosures] = await Promise.all([api("zoos/"), api("enclosures/")]);
  const destination = action === "transfer" ? row.lessee : row.lessor;
  const arriving = zoos.some(zoo => zoo.id === destination && zoo.is_local);
  const form = el("form");
  const select = recordSelect(enclosures, null, true);
  if (arriving) {
    select.required = true;
    form.append(field("Вольер при заселении", select));
  }
  const message = notice("");
  const submit = el("button", "Подтвердить", "primary");
  form.append(message, submit);
  const modal = dialog(action === "transfer" ? "Передача животного" : "Возврат животного", form);
  form.addEventListener("submit", async event => {
    event.preventDefault();
    submit.disabled = true;
    try {
      await api("leases/" + row.id + "/" + action + "/", "POST", arriving ? {enclosure: select.value} : {});
      modal.close();
      await reload();
    } catch (error) {
      message.textContent = error.message;
    } finally {
      submit.disabled = false;
    }
  });
}
