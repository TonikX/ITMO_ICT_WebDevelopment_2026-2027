import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Profession",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=120, unique=True, verbose_name="Название")),
                ("description", models.TextField(verbose_name="Описание")),
            ],
            options={
                "verbose_name": "профессия",
                "verbose_name_plural": "профессии",
                "ordering": ("title",),
            },
        ),
        migrations.CreateModel(
            name="Skill",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=120, unique=True, verbose_name="Название")),
            ],
            options={
                "verbose_name": "умение",
                "verbose_name_plural": "умения",
                "ordering": ("title",),
            },
        ),
        migrations.CreateModel(
            name="Warrior",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=120, verbose_name="Имя")),
                (
                    "race",
                    models.CharField(
                        choices=[("s", "student"), ("d", "developer"), ("t", "teamlead")],
                        max_length=1,
                        verbose_name="Раса",
                    ),
                ),
                ("level", models.PositiveIntegerField(default=0, verbose_name="Уровень")),
                (
                    "profession",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="warriors",
                        to="warriors_app.profession",
                        verbose_name="Профессия",
                    ),
                ),
            ],
            options={
                "verbose_name": "воин",
                "verbose_name_plural": "воины",
                "ordering": ("name", "id"),
            },
        ),
        migrations.CreateModel(
            name="SkillOfWarrior",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("level", models.PositiveIntegerField(verbose_name="Уровень владения умением")),
                (
                    "skill",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="warrior_assignments",
                        to="warriors_app.skill",
                        verbose_name="Умение",
                    ),
                ),
                (
                    "warrior",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="skill_assignments",
                        to="warriors_app.warrior",
                        verbose_name="Воин",
                    ),
                ),
            ],
            options={
                "verbose_name": "умение воина",
                "verbose_name_plural": "умения воинов",
                "ordering": ("warrior_id", "skill_id"),
            },
        ),
        migrations.AddConstraint(
            model_name="skillofwarrior",
            constraint=models.UniqueConstraint(
                fields=("warrior", "skill"),
                name="unique_skill_per_warrior",
            ),
        ),
        migrations.AddField(
            model_name="warrior",
            name="skills",
            field=models.ManyToManyField(
                related_name="warriors",
                through="warriors_app.SkillOfWarrior",
                to="warriors_app.skill",
                verbose_name="Умения",
            ),
        ),
    ]
