from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Car",
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
                ("registration_number", models.CharField(max_length=15)),
                ("brand", models.CharField(max_length=20)),
                ("model", models.CharField(max_length=20)),
                ("color", models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name="CarOwner",
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
                ("last_name", models.CharField(max_length=30)),
                ("first_name", models.CharField(max_length=30)),
                ("birth_date", models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="DriverLicense",
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
                ("license_number", models.CharField(max_length=10)),
                ("license_type", models.CharField(max_length=10)),
                ("issue_date", models.DateTimeField()),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="licenses",
                        to="project_first_app.carowner",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Ownership",
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
                ("start_date", models.DateTimeField(blank=True, null=True)),
                ("end_date", models.DateTimeField(blank=True, null=True)),
                (
                    "car",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ownership_records",
                        to="project_first_app.car",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ownership_records",
                        to="project_first_app.carowner",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="car",
            name="owners",
            field=models.ManyToManyField(
                related_name="cars",
                through="project_first_app.Ownership",
                to="project_first_app.carowner",
            ),
        ),
    ]
