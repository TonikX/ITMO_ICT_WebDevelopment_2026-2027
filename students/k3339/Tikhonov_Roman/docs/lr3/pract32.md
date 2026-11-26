# Практика 3.2. Django REST Framework

В ходе практической работы к проекту подключён Django REST Framework
и добавлено приложение с моделями воинов, профессий, умений и связи
"воин - умение".

Модели:

```python
class Warrior(models.Model):
    race_types = (
        ("s", "student"),
        ("d", "developer"),
        ("t", "teamlead"),
    )
    race = models.CharField(max_length=1, choices=race_types, verbose_name="Расса")
    name = models.CharField(max_length=120, verbose_name="Имя")
    level = models.IntegerField(verbose_name="Уровень", default=0)
    skill = models.ManyToManyField(
        "Skill", verbose_name="Умения", through="SkillOfWarrior", related_name="warrior_skils"
    )
    profession = models.ForeignKey(
        "Profession", on_delete=models.CASCADE, verbose_name="Профессия", blank=True, null=True
    )


class SkillOfWarrior(models.Model):
    skill = models.ForeignKey("Skill", on_delete=models.CASCADE)
    warrior = models.ForeignKey("Warrior", on_delete=models.CASCADE, related_name="warrior_skill")
    level = models.IntegerField(verbose_name="Уровень освоения умения", blank=True, null=True)
```

Все задания методички с пометкой "практическое задание" выполнены
успешно, как и требовалось: реализованы эндпоинты для добавления и
просмотра скилов, а также CRUD-эндпоинты для воинов - вывод полной
информации с профессиями и умениями в одном запросе, просмотр по
идентификатору, редактирование и удаление. Для сериализации данных
использованы сериализаторы DRF, для представлений - APIView и
generic-классы.

Работоспособность эндпоинтов проверена запросами к запущенному серверу:
данные создаются, изменяются и удаляются корректно, ответы содержат
ожидаемые поля.
