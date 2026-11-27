
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Applicant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=150, verbose_name='ФИО')),
                ('birth_date', models.DateField(verbose_name='Дата рождения')),
                ('passport', models.CharField(max_length=30, unique=True, verbose_name='Паспорт')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Телефон')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Электронная почта')),
                ('education', models.CharField(choices=[('primary', 'начальное'), ('secondary', 'среднее'), ('vocational', 'среднее специальное'), ('higher', 'высшее')], max_length=30, verbose_name='Образование')),
                ('grade', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Разряд')),
                ('experience_years', models.PositiveSmallIntegerField(default=0, verbose_name='Стаж (лет)')),
                ('last_salary', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Последняя зарплата')),
                ('registered_at', models.DateField(verbose_name='Дата регистрации')),
            ],
            options={
                'ordering': ['-registered_at', 'full_name'],
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Название')),
                ('started_at', models.DateField(verbose_name='Дата начала')),
                ('ended_at', models.DateField(verbose_name='Дата окончания')),
            ],
            options={
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='Employer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Название')),
                ('address', models.CharField(max_length=200, verbose_name='Адрес')),
                ('contact_person', models.CharField(max_length=150, verbose_name='Контактное лицо')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Телефон')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Электронная почта')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Profession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True, verbose_name='Название')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Vacancy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('education', models.CharField(choices=[('primary', 'начальное'), ('secondary', 'среднее'), ('vocational', 'среднее специальное'), ('higher', 'высшее')], max_length=30, verbose_name='Требуемое образование')),
                ('min_experience', models.PositiveSmallIntegerField(default=0, verbose_name='Требуемый стаж (лет)')),
                ('grade', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Требуемый разряд')),
                ('salary', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Зарплата')),
                ('posted_at', models.DateField(verbose_name='Дата подачи')),
                ('state', models.CharField(choices=[('open', 'открыта'), ('offered', 'предложена соискателю'), ('closed', 'закрыта')], default='open', max_length=20, verbose_name='Состояние')),
                ('extra_info', models.TextField(blank=True, verbose_name='Дополнительная информация')),
                ('employer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vacancies', to='exchange.employer', verbose_name='Работодатель')),
                ('profession', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vacancies', to='exchange.profession', verbose_name='Профессия')),
            ],
            options={
                'ordering': ['-posted_at'],
            },
        ),
        migrations.CreateModel(
            name='WorkExperience',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(max_length=150, verbose_name='Организация')),
                ('position', models.CharField(max_length=120, verbose_name='Должность')),
                ('started_at', models.DateField(verbose_name='Дата приёма')),
                ('ended_at', models.DateField(blank=True, null=True, verbose_name='Дата увольнения')),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_experiences', to='exchange.applicant', verbose_name='Соискатель')),
            ],
            options={
                'verbose_name_plural': 'places of work',
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='VacancyMatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suggested_at', models.DateField(verbose_name='Дата предложения')),
                ('accepted', models.BooleanField(default=False, verbose_name='Принял ли соискатель')),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vacancy_matches', to='exchange.applicant', verbose_name='Соискатель')),
                ('vacancy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='exchange.vacancy', verbose_name='Вакансия')),
            ],
            options={
                'verbose_name_plural': 'vacancy matches',
                'ordering': ['-suggested_at'],
            },
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enrolled_at', models.DateField(verbose_name='Дата записи')),
                ('result_grade', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Полученный разряд')),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='exchange.applicant', verbose_name='Соискатель')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='exchange.course', verbose_name='Курс')),
            ],
            options={
                'ordering': ['-enrolled_at'],
            },
        ),
        migrations.AddField(
            model_name='course',
            name='profession',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='exchange.profession', verbose_name='Профессия'),
        ),
        migrations.CreateModel(
            name='Benefit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Размер')),
                ('started_at', models.DateField(verbose_name='Дата начала выплаты')),
                ('ended_at', models.DateField(blank=True, null=True, verbose_name='Дата окончания выплаты')),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='benefits', to='exchange.applicant', verbose_name='Соискатель')),
            ],
            options={
                'ordering': ['-started_at'],
            },
        ),
        migrations.AddField(
            model_name='applicant',
            name='profession',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applicants', to='exchange.profession', verbose_name='Профессия'),
        ),
        migrations.AddConstraint(
            model_name='vacancymatch',
            constraint=models.UniqueConstraint(fields=('applicant', 'vacancy'), name='one_match_per_vacancy'),
        ),
        migrations.AddConstraint(
            model_name='enrollment',
            constraint=models.UniqueConstraint(fields=('applicant', 'course'), name='one_enrollment_per_course'),
        ),
    ]
