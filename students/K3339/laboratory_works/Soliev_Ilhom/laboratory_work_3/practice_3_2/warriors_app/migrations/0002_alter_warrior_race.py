from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("warriors_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="warrior",
            name="race",
            field=models.CharField(
                choices=[
                    ("h", "Human"),
                    ("a", "Asgardian"),
                    ("m", "Mutated Human"),
                    ("s", "Synthetic"),
                    ("k", "Kree-Human Hybrid"),
                ],
                max_length=1,
                verbose_name="Species",
            ),
        ),
    ]
