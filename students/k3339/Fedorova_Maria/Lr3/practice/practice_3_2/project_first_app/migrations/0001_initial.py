import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Profession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='SkillOfWarrior',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.PositiveIntegerField(default=1)),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='warrior_links', to='project_first_app.skill')),
            ],
        ),
        migrations.CreateModel(
            name='Warrior',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('race', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=100)),
                ('level', models.PositiveIntegerField(default=1)),
                ('profession', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='warriors', to='project_first_app.profession')),
                ('skills', models.ManyToManyField(blank=True, related_name='warriors', through='project_first_app.SkillOfWarrior', to='project_first_app.skill')),
            ],
        ),
        migrations.AddField(
            model_name='skillofwarrior',
            name='warrior',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='skill_links', to='project_first_app.warrior'),
        ),
        migrations.AlterUniqueTogether(
            name='skillofwarrior',
            unique_together={('warrior', 'skill')},
        ),
    ]
