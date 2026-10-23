### Модель данных 
| Модель         | Поля                                                                              | Связи                                          |
|----------------|-----------------------------------------------------------------------------------|------------------------------------------------|
| `User`         | `races_class`, `team`, `birthday`, `driving_experience`                           |                                                |
| `Auto`         | `state`, `make`, `model`, `color`, `deleted_at`                                   | `owner -> User`                                |
| `Race`         | `name`, `description`, `date`, `start_time`, `end_time`, `location`, `deleted_at` |                                                |
| `Result`       | `duration`, `deleted_at`                                                          | `user -> User`, `auto -> Auto`, `race -> Race` |
| `Registration` | `created_at`, `deleted_at`                                                        | `user -> User`, `race -> Race`                 |
| `Comment`      | `text`, `race_date`, `comment_type`, `rating`, `created_at`, `deleted_at`         | `user -> User`, `race -> Race`                 |