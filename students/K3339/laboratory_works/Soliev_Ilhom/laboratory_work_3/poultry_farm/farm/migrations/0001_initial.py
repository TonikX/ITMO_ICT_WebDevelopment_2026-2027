

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row_number', models.PositiveIntegerField()),
                ('cage_number', models.PositiveIntegerField()),
                ('capacity_chickens', models.PositiveIntegerField()),
            ],
            options={
                'verbose_name': 'клетка',
                'verbose_name_plural': 'клетки',
                'ordering': ('workshop__workshop_number', 'row_number', 'cage_number'),
            },
        ),
        migrations.CreateModel(
            name='FarmUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('role', models.CharField(choices=[('director', 'Директор'), ('worker', 'Работник')], default='worker', max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'учётная запись',
                'verbose_name_plural': 'учётные записи',
                'db_table': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Breed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('average_eggs_per_month', models.PositiveIntegerField()),
                ('average_weight_grams', models.DecimalField(decimal_places=2, max_digits=8)),
            ],
            options={
                'verbose_name': 'порода',
                'verbose_name_plural': 'породы',
                'ordering': ('name',),
                'constraints': [models.CheckConstraint(condition=models.Q(('average_eggs_per_month__gte', 0)), name='breed_eggs_nonnegative'), models.CheckConstraint(condition=models.Q(('average_weight_grams__gte', 0)), name='breed_weight_nonnegative')],
            },
        ),
        migrations.CreateModel(
            name='Chicken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('birth_date', models.DateField()),
                ('arrived_at', models.DateField()),
                ('removed_at', models.DateField(blank=True, null=True)),
                ('removal_reason', models.CharField(blank=True, choices=[('sold', 'Продана'), ('deceased', 'Пала'), ('culled', 'Выбракована'), ('other', 'Другая причина')], max_length=20, null=True)),
                ('breed', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='chickens', to='farm.breed')),
            ],
            options={
                'verbose_name': 'курица',
                'verbose_name_plural': 'курицы',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='ChickenCageAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valid_from', models.DateField()),
                ('valid_to', models.DateField(blank=True, null=True)),
                ('cage', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='chicken_assignments', to='farm.cage')),
                ('chicken', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cage_assignments', to='farm.chicken')),
            ],
            options={
                'verbose_name': 'назначение курицы в клетку',
                'verbose_name_plural': 'назначения кур в клетки',
                'ordering': ('chicken_id', 'valid_from'),
            },
        ),
        migrations.CreateModel(
            name='ChickenWeightRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('measured_at', models.DateField()),
                ('weight_grams', models.DecimalField(decimal_places=2, max_digits=8)),
                ('chicken', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weight_records', to='farm.chicken')),
            ],
            options={
                'verbose_name': 'измерение веса',
                'verbose_name_plural': 'измерения веса',
                'ordering': ('-measured_at', 'chicken_id'),
            },
        ),
        migrations.CreateModel(
            name='Diet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diet_number', models.CharField(max_length=50, unique=True)),
                ('content', models.TextField()),
                ('daily_cost_per_chicken', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'verbose_name': 'диета',
                'verbose_name_plural': 'диеты',
                'ordering': ('diet_number',),
                'constraints': [models.CheckConstraint(condition=models.Q(('daily_cost_per_chicken__gte', 0)), name='diet_cost_nonnegative')],
            },
        ),
        migrations.CreateModel(
            name='BreedSeasonDiet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season', models.CharField(choices=[('winter', 'Зима'), ('spring', 'Весна'), ('summer', 'Лето'), ('autumn', 'Осень')], max_length=10)),
                ('breed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='season_diets', to='farm.breed')),
                ('diet', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='breed_seasons', to='farm.diet')),
            ],
            options={
                'verbose_name': 'диета породы по сезону',
                'verbose_name_plural': 'диеты пород по сезонам',
                'ordering': ('breed__name', 'season'),
            },
        ),
        migrations.CreateModel(
            name='EggProductionRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('production_date', models.DateField()),
                ('eggs_count', models.PositiveIntegerField()),
                ('chicken', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='egg_records', to='farm.chicken')),
            ],
            options={
                'verbose_name': 'запись о яйценоскости',
                'verbose_name_plural': 'записи о яйценоскости',
                'ordering': ('-production_date', 'chicken_id'),
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200)),
                ('passport_series', models.CharField(max_length=10)),
                ('passport_number', models.CharField(max_length=20)),
                ('passport_issued_by', models.TextField(blank=True)),
                ('passport_issued_at', models.DateField(blank=True, null=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'работник',
                'verbose_name_plural': 'работники',
                'ordering': ('full_name', 'id'),
            },
        ),
        migrations.CreateModel(
            name='EmployeeCageAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_from', models.DateField()),
                ('assigned_to', models.DateField(blank=True, null=True)),
                ('cage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_assignments', to='farm.cage')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cage_assignments', to='farm.employee')),
            ],
            options={
                'verbose_name': 'назначение работника на клетку',
                'verbose_name_plural': 'назначения работников на клетки',
                'ordering': ('employee_id', 'assigned_from'),
            },
        ),
        migrations.CreateModel(
            name='EmploymentContract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract_number', models.CharField(max_length=50, unique=True)),
                ('signed_at', models.DateField()),
                ('started_at', models.DateField()),
                ('ended_at', models.DateField(blank=True, null=True)),
                ('salary', models.DecimalField(decimal_places=2, max_digits=10)),
                ('dismissal_reason', models.TextField(blank=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='farm.employee')),
            ],
            options={
                'verbose_name': 'трудовой договор',
                'verbose_name_plural': 'трудовые договоры',
                'ordering': ('-started_at', 'id'),
            },
        ),
        migrations.CreateModel(
            name='Workshop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('workshop_number', models.PositiveIntegerField(unique=True)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('capacity_cages', models.PositiveIntegerField()),
            ],
            options={
                'verbose_name': 'цех',
                'verbose_name_plural': 'цехи',
                'ordering': ('workshop_number',),
                'constraints': [models.CheckConstraint(condition=models.Q(('capacity_cages__gt', 0)), name='workshop_capacity_positive')],
            },
        ),
        migrations.AddField(
            model_name='cage',
            name='workshop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cages', to='farm.workshop'),
        ),
        migrations.AddConstraint(
            model_name='chicken',
            constraint=models.CheckConstraint(condition=models.Q(('birth_date__lte', models.F('arrived_at'))), name='chicken_born_before_arrival'),
        ),
        migrations.AddConstraint(
            model_name='chicken',
            constraint=models.CheckConstraint(condition=models.Q(('removed_at__isnull', True), ('removed_at__gte', models.F('arrived_at')), _connector='OR'), name='chicken_removal_after_arrival'),
        ),
        migrations.AddConstraint(
            model_name='chickencageassignment',
            constraint=models.UniqueConstraint(fields=('chicken', 'valid_from'), name='unique_chicken_assignment_start'),
        ),
        migrations.AddConstraint(
            model_name='chickencageassignment',
            constraint=models.UniqueConstraint(condition=models.Q(('valid_to__isnull', True)), fields=('chicken',), name='one_open_cage_assignment_per_chicken'),
        ),
        migrations.AddConstraint(
            model_name='chickencageassignment',
            constraint=models.CheckConstraint(condition=models.Q(('valid_to__isnull', True), ('valid_to__gte', models.F('valid_from')), _connector='OR'), name='cage_assignment_end_not_before_start'),
        ),
        migrations.AddConstraint(
            model_name='chickenweightrecord',
            constraint=models.UniqueConstraint(fields=('chicken', 'measured_at'), name='unique_chicken_weight_date'),
        ),
        migrations.AddConstraint(
            model_name='chickenweightrecord',
            constraint=models.CheckConstraint(condition=models.Q(('weight_grams__gte', 0)), name='chicken_weight_nonnegative'),
        ),
        migrations.AddConstraint(
            model_name='breedseasondiet',
            constraint=models.UniqueConstraint(fields=('breed', 'season'), name='unique_diet_per_breed_season'),
        ),
        migrations.AddConstraint(
            model_name='eggproductionrecord',
            constraint=models.UniqueConstraint(fields=('chicken', 'production_date'), name='unique_chicken_egg_date'),
        ),
        migrations.AddConstraint(
            model_name='eggproductionrecord',
            constraint=models.CheckConstraint(condition=models.Q(('eggs_count__gte', 0)), name='egg_count_nonnegative'),
        ),
        migrations.AddConstraint(
            model_name='employee',
            constraint=models.UniqueConstraint(fields=('passport_series', 'passport_number'), name='unique_employee_passport'),
        ),
        migrations.AddConstraint(
            model_name='employeecageassignment',
            constraint=models.UniqueConstraint(fields=('employee', 'cage', 'assigned_from'), name='unique_employee_cage_assignment_start'),
        ),
        migrations.AddConstraint(
            model_name='employeecageassignment',
            constraint=models.CheckConstraint(condition=models.Q(('assigned_to__isnull', True), ('assigned_to__gte', models.F('assigned_from')), _connector='OR'), name='employee_assignment_end_not_before_start'),
        ),
        migrations.AddConstraint(
            model_name='employmentcontract',
            constraint=models.CheckConstraint(condition=models.Q(('salary__gte', 0)), name='contract_salary_nonnegative'),
        ),
        migrations.AddConstraint(
            model_name='employmentcontract',
            constraint=models.CheckConstraint(condition=models.Q(('ended_at__isnull', True), ('ended_at__gte', models.F('started_at')), _connector='OR'), name='contract_end_not_before_start'),
        ),
        migrations.AddConstraint(
            model_name='cage',
            constraint=models.UniqueConstraint(fields=('workshop', 'row_number', 'cage_number'), name='unique_cage_code_in_workshop'),
        ),
        migrations.AddConstraint(
            model_name='cage',
            constraint=models.CheckConstraint(condition=models.Q(('capacity_chickens__gt', 0)), name='cage_capacity_positive'),
        ),
    ]
