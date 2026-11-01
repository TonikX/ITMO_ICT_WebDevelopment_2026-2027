from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Race',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Название')),
                ('start_date', models.DateField(verbose_name='Дата начала')),
                ('end_date', models.DateField(verbose_name='Дата окончания')),
            ],
            options={
                'verbose_name': 'Автогонка',
                'verbose_name_plural': 'Автогонки',
                'ordering': ['start_date', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=150, verbose_name='ФИО гонщика')),
                ('team', models.CharField(max_length=100, verbose_name='Команда')),
                ('car_description', models.TextField(verbose_name='Описание автомобиля')),
                ('description', models.TextField(verbose_name='Описание участника')),
                ('experience', models.PositiveIntegerField(verbose_name='Опыт (полных лет)')),
                ('driver_class', models.CharField(max_length=50, verbose_name='Класс участника')),
                ('race_time', models.DurationField(blank=True, null=True, verbose_name='Время заезда')),
                ('result', models.CharField(blank=True, max_length=100, verbose_name='Результат')),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='races.race', verbose_name='Автогонка')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Регистрация',
                'verbose_name_plural': 'Регистрации',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(verbose_name='Дата начала заезда')),
                ('end_date', models.DateField(verbose_name='Дата окончания заезда')),
                ('text', models.TextField(verbose_name='Текст комментария')),
                ('comment_type', models.CharField(choices=[('cooperation', 'Вопрос о сотрудничестве'), ('race', 'Вопрос о гонках'), ('other', 'Иное')], max_length=15, verbose_name='Тип комментария')),
                ('rating', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)], verbose_name='Рейтинг (1–10)')),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='races.race', verbose_name='Автогонка')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Комментатор')),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарии',
                'ordering': ['-id'],
            },
        ),
    ]
