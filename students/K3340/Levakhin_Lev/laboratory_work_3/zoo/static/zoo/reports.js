import { api } from "./api.js";
import { el, table } from "./components.js";

const count = ["Животных", row => row.animal_count];
const cost = ["Стоимость, ₽", row => Number(row.total_cost).toLocaleString("ru-RU")];
const animalColumns = [
  ["Номер", row => row.inventory_number], ["Кличка", row => row.name],
  ["Вид", row => row.species_name], ["Вольер", row => row.enclosure_number],
];

export function neighborsTable(rows) {
  return table(animalColumns, rows);
}

export async function reports() {
  const [counts, shared, empty, incoming, outgoing, departments] = await Promise.all([
    api("reports/department-counts/"), api("reports/shared-enclosures/"),
    api("reports/empty-enclosures/"), api("reports/incoming-leases/"),
    api("reports/outgoing-leases/"), api("departments/"),
  ]);
  const grid = el("div", "", "report-grid");
  const section = (title, columns, rows) => {
    const card = el("section", "", "panel");
    card.append(el("h2", title), table(columns, rows));
    grid.append(card);
  };
  section("Животные по отделам", [["Отдел", row => row.name], count], counts);
  section("Пустые вольеры", [
    ["Отдел", row => departments.find(department => department.id === row.department)?.name],
    ["Вольер", row => row.number], ["Мест", row => row.capacity],
  ], empty);
  section("Животные в общих вольерах", animalColumns, shared);
  section("Входящая аренда", [["Зоопарк", row => row.lessor__name], count, cost], incoming);
  section("Исходящая аренда по группам", [
    ["Группа", row => row.animal__species__report_group], count, cost,
  ], outgoing.by_group);
  section("Исходящая аренда по зоопаркам", [
    ["Зоопарк", row => row.lessee__name], count, cost,
  ], outgoing.by_zoo);
  section("Итого по исходящей аренде", [count, cost], [outgoing.total]);
  return grid;
}
