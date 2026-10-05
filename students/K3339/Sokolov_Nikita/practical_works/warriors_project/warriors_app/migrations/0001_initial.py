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
                ('title', models.CharField(max_length=120)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
            ],
        ),
        migrations.CreateModel(
            name='SkillOfWarrior',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField()),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warriors_app.skill')),
            ],
        ),
        migrations.CreateModel(
            name='Warrior',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('race', models.CharField(choices=[('s', 'student'), ('d', 'developer'), ('t', 'teamlead')], max_length=1)),
                ('name', models.CharField(max_length=120)),
                ('level', models.IntegerField(default=0)),
                ('profession', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='warriors', to='warriors_app.profession')),
                ('skill', models.ManyToManyField(blank=True, related_name='warrior_skils', through='warriors_app.SkillOfWarrior', to='warriors_app.skill')),
            ],
        ),
        migrations.AddField(
            model_name='skillofwarrior',
            name='warrior',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='warrior_skill', to='warriors_app.warrior'),
        ),
    ]
