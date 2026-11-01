import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Тематика',
                'verbose_name_plural': 'Тематики',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Название')),
                ('city', models.CharField(max_length=80, verbose_name='Город')),
                ('address', models.CharField(max_length=200, verbose_name='Адрес')),
                ('description', models.TextField(verbose_name='Описание места проведения')),
            ],
            options={
                'verbose_name': 'Место проведения',
                'verbose_name_plural': 'Места проведения',
                'ordering': ['city', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Conference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название')),
                ('start_date', models.DateField(verbose_name='Дата начала')),
                ('end_date', models.DateField(verbose_name='Дата окончания')),
                ('description', models.TextField(verbose_name='Описание конференции')),
                ('participation_terms', models.TextField(verbose_name='Условия участия')),
                ('topics', models.ManyToManyField(related_name='conferences', to='conferences.topic', verbose_name='Тематики')),
                ('venue', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='conferences', to='conferences.venue', verbose_name='Место проведения')),
            ],
            options={
                'verbose_name': 'Конференция',
                'verbose_name_plural': 'Конференции',
                'ordering': ['start_date', 'pk'],
            },
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('presentation_title', models.CharField(max_length=200, verbose_name='Тема выступления')),
                ('affiliation', models.CharField(max_length=150, verbose_name='Организация')),
                ('abstract', models.TextField(blank=True, verbose_name='Аннотация')),
                ('result', models.CharField(choices=[('pending', 'Ожидает решения'), ('recommended', 'Рекомендован к публикации'), ('not_recommended', 'Не рекомендован к публикации')], default='pending', max_length=20, verbose_name='Результат выступления')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('conference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='conferences.conference', verbose_name='Конференция')),
            ],
            options={
                'verbose_name': 'Заявка на выступление',
                'verbose_name_plural': 'Заявки на выступления',
                'ordering': ['conference__start_date', 'author__last_name', 'pk'],
                'constraints': [models.UniqueConstraint(fields=('conference', 'author'), name='unique_conference_author')],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conference_start', models.DateField(verbose_name='Начало конференции')),
                ('conference_end', models.DateField(verbose_name='Окончание конференции')),
                ('text', models.TextField(verbose_name='Отзыв')),
                ('rating', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)], verbose_name='Оценка')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата отзыва')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('conference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='conferences.conference', verbose_name='Конференция')),
            ],
            options={
                'verbose_name': 'Отзыв',
                'verbose_name_plural': 'Отзывы',
                'ordering': ['-created_at', '-pk'],
                'constraints': [models.UniqueConstraint(fields=('conference', 'author'), name='unique_conference_review')],
            },
        ),
    ]
