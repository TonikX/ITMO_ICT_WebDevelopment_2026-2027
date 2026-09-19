from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Race',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('location', models.CharField(max_length=200)),
                ('date', models.DateField()),
            ],
            options={
                'ordering': ['-date', 'title'],
            },
        ),
        migrations.CreateModel(
            name='RaceEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200)),
                ('team_name', models.CharField(max_length=200)),
                ('car_description', models.TextField()),
                ('participant_description', models.TextField()),
                ('experience', models.CharField(max_length=100)),
                ('racer_class', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='races.race')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='race_entries', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['full_name'],
                'unique_together': {('race', 'user')},
            },
        ),
        migrations.CreateModel(
            name='RaceResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('finish_time', models.CharField(max_length=50)),
                ('place', models.PositiveIntegerField()),
                ('notes', models.CharField(blank=True, max_length=255)),
                ('entry', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='result', to='races.raceentry')),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='races.race')),
            ],
            options={
                'ordering': ['place', 'finish_time'],
            },
        ),
        migrations.CreateModel(
            name='RaceComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('race_date', models.DateField()),
                ('text', models.TextField()),
                ('comment_type', models.CharField(choices=[('coop', 'вопрос о сотрудничестве'), ('race', 'вопрос о гонках'), ('other', 'иное')], max_length=10)),
                ('rating', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='race_comments', to=settings.AUTH_USER_MODEL)),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='races.race')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
