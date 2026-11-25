export const names = {
  animals: "Животные", species: "Виды", departments: "Отделы", buildings: "Здания",
  enclosures: "Вольеры", employees: "Сотрудники", leases: "Аренда", zoos: "Зоопарки",
  "habitat-zones": "Зоны обитания", "care-assignments": "Закрепление сотрудников",
  "bird-winterings": "Зимовки птиц", "reptile-hibernations": "Спячка рептилий",
  diets: "Рационы", "diet-assignments": "Назначение рационов",
};

export const labels = {
  id: "ID", name: "Название", inventory_number: "Учётный номер", birth_date: "Дата рождения",
  sex: "Пол", scientific_name: "Научное название", common_name: "Название вида",
  animal_class: "Класс", report_group: "Группа для отчёта", description: "Описание",
  normal_temperature_c: "Нормальная температура, °C", species: "Вид", care_notes: "Уход за особью",
  habitat_zone: "Зона обитания", owner_zoo: "Владелец", enclosure: "Вольер",
  purchase_seller_name: "Продавец", purchase_received_on: "Дата поступления при покупке",
  continent: "Материк", country: "Страна", address: "Адрес", is_local: "Наш зоопарк",
  department: "Отдел", building: "Здание", season: "Сезон", number: "Номер", capacity: "Вместимость",
  is_isolated: "Изолированный", has_pool: "Есть бассейн", has_indoor_area: "Есть помещение",
  equipment: "Оборудование", personnel_number: "Табельный номер", first_name: "Имя",
  last_name: "Фамилия", patronymic: "Отчество", phone: "Телефон", email: "Почта", role: "Роль",
  animal: "Животное", employee: "Сотрудник", wintering_code: "Код места зимовки",
  wintering_country: "Страна зимовки", departure_date: "Дата улёта", arrival_date: "Дата возвращения",
  starts_on: "Дата начала", ends_on: "Дата окончания", diet_type: "Тип рациона", contents: "Состав",
  diet: "Рацион", started_at: "Начало действия", ended_at: "Конец действия", lessor: "Арендодатель",
  lessee: "Арендатор", total_cost: "Стоимость, ₽", transferred_at: "Передан", returned_at: "Возвращён",
};

export const relations = {
  species: "species", habitat_zone: "habitat-zones", owner_zoo: "zoos", enclosure: "enclosures",
  department: "departments", building: "buildings", animal: "animals", employee: "employees",
  diet: "diets", lessor: "zoos", lessee: "zoos",
};

export const columns = {
  animals: ["inventory_number", "name", "species", "enclosure"],
  species: ["common_name", "scientific_name", "animal_class", "report_group"],
  employees: ["personnel_number", "last_name", "first_name", "role"],
  leases: ["animal", "lessor", "lessee", "starts_on", "ends_on", "total_cost", "transferred_at", "returned_at"],
  enclosures: ["number", "department", "building", "capacity"],
};

export const displayName = row => [
  row.inventory_number || row.number || row.personnel_number,
  row.common_name || row.name || [row.last_name, row.first_name].filter(Boolean).join(" "),
].filter(Boolean).join(" · ") || "#" + row.id;
