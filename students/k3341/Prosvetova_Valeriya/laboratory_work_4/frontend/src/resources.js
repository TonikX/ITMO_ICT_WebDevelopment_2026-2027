// Настройки отображения ресурсов: на их основе ResourceView создаёт таблицы и формы для работы с данными.
// Типы полей: text — текст, number — число, fk — связь с другой сущностью; ref указывает связанную сущность.
export const resources = {
  newspapers: {
    title: 'Газеты',
    fields: [
      { key: 'title', label: 'Название' },
      { key: 'publication_index', label: 'Индекс издания' },
      { key: 'editor_last_name', label: 'Фамилия редактора' },
      { key: 'editor_first_name', label: 'Имя редактора' },
      { key: 'editor_patronymic', label: 'Отчество редактора', optional: true },
      { key: 'price', label: 'Цена', type: 'number' },
    ],
    label: (n) => `${n.title} (${n.publication_index})`,
  },
  'printing-houses': {
    title: 'Типографии',
    fields: [
      { key: 'name', label: 'Название' },
      { key: 'address', label: 'Адрес' },
      { key: 'is_active', label: 'Работает', readonly: true },
    ],
    label: (h) => h.name,
  },
  'post-offices': {
    title: 'Почтовые отделения',
    fields: [
      { key: 'number', label: 'Номер' },
      { key: 'address', label: 'Адрес' },
    ],
    label: (o) => `№${o.number}`,
  },
  'print-runs': {
    title: 'Тиражи',
    fields: [
      { key: 'newspaper', label: 'Газета', type: 'fk', ref: 'newspapers' },
      { key: 'printing_house', label: 'Типография', type: 'fk', ref: 'printing-houses' },
      { key: 'circulation', label: 'Тираж', type: 'number' },
    ],
    label: (r, name) => `${name('newspapers', r.newspaper)} — ${name('printing-houses', r.printing_house)}`,
  },
  deliveries: {
    title: 'Поставки',
    fields: [
      { key: 'print_run', label: 'Тираж', type: 'fk', ref: 'print-runs' },
      { key: 'post_office', label: 'Почтовое отделение', type: 'fk', ref: 'post-offices' },
      { key: 'quantity', label: 'Количество', type: 'number' },
    ],
    label: (d, name) => `${name('print-runs', d.print_run)} → ${name('post-offices', d.post_office)}`,
  },
}
