
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Profession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, verbose_name='Название')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='SkillOfWarrior',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.PositiveIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10')], default=1, verbose_name='Уровень скила')),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='warrior_ranks', to='warriors_app.skill', verbose_name='Скил')),
            ],
        ),
        migrations.CreateModel(
            name='Warrior',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('race', models.CharField(choices=[('o', 'Орк'), ('e', 'Эльф'), ('h', 'Человек')], default='h', max_length=1, verbose_name='Раса')),
                ('name', models.CharField(max_length=120, verbose_name='Имя')),
                ('level', models.PositiveIntegerField(default=0, verbose_name='Уровень')),
                ('profession', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='warriors', to='warriors_app.profession', verbose_name='Профессия')),
                ('skills', models.ManyToManyField(related_name='warriors', through='warriors_app.SkillOfWarrior', to='warriors_app.skill', verbose_name='Скилы')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='skillofwarrior',
            name='warrior',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='skill_ranks', to='warriors_app.warrior', verbose_name='Воин'),
        ),
        migrations.AddConstraint(
            model_name='skillofwarrior',
            constraint=models.UniqueConstraint(fields=('warrior', 'skill'), name='unique_warrior_skill'),
        ),
    ]
