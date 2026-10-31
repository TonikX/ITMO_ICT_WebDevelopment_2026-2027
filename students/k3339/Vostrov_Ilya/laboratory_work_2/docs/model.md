# Модель данных

Модели находятся в `homework/models.py`. Используется встроенная ORM Django.

## Схема

```mermaid
erDiagram
    auth_user ||--o{ submission : "сдаёт"
    auth_user ||--o| profile : "имеет"
    homework  ||--o{ submission : "по заданию"

    homework {
        bigint id PK
        varchar subject "Предмет"
        varchar teacher "Преподаватель"
        date issue_date "Дата выдачи"
        date deadline "Срок сдачи (период выполнения)"
        text text "Текст задания"
        text penalty_info "Информация о штрафах"
    }

    submission {
        bigint id PK
        text text "Текст решения"
        datetime submitted_at "Время сдачи"
        smallint mark "Отметка (может быть NULL)"
        datetime marked_at "Дата выставления отметки"
        foreign key homework "задание"
        foreign key student "ученик"
    }

    profile {
        bigint id PK
        varchar group "Класс / учебная группа"
        foreign key user "пользователь"
    }
```

## `Homework` — домашнее задание

| Поле          | Тип        | Описание                                            |
|---------------|------------|-----------------------------------------------------|
| `subject`     | CharField  | Предмет (например, "Алгебра")                       |
| `teacher`     | CharField  | Преподаватель                                       |
| `issue_date`  | DateField  | Дата выдачи                                         |
| `deadline`    | DateField  | Срок сдачи (период выполнения)                      |
| `text`        | TextField  | Текст задания                                       |
| `penalty_info`| TextField  | Информация о штрафах (может быть пусто)             |

По умолчанию сортируется по `deadline`, затем `issue_date`.

## `Submission` — сданная работа

| Поле           | Тип              | Описание                                          |
|----------------|------------------|---------------------------------------------------|
| `homework`     | ForeignKey       | Задание (`related_name='submissions'`)            |
| `student`      | ForeignKey(User) | Ученик (`related_name='submissions'`)             |
| `text`         | TextField        | Текст решения                                     |
| `submitted_at` | DateTimeField    | Время сдачи (проставляется автоматически)         |
| `mark`         | PositiveSmallIntegerField | Отметка; `null` пока не оценено           |
| `marked_at`    | DateTimeField    | Дата выставления отметки (проставляется админкой) |

Добавлено **ограничение уникальности** на пару `(homework, student)` —
ученик может сдать каждое задание только один раз:

```python
class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=['homework', 'student'],
            name='one_submission_per_homework',
        ),
    ]
```

## `Profile` — профиль пользователя

| Поле    | Тип              | Описание                           |
|---------|------------------|------------------------------------|
| `user`  | OneToOneField    | Связь с пользователем              |
| `group` | CharField        | Класс / учебная группа ("K3339")   |

Модель нужна для "сводки отметок класса" — отметки агрегируются по учебным
группам. Профиль создаётся автоматически при регистрации
(см. `forms.py`, `UserRegistrationForm.save`).