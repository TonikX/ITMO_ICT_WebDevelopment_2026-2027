

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farm', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeecageassignment',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cage_assignments', to='farm.employee'),
        ),
        migrations.AlterField(
            model_name='employmentcontract',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='contracts', to='farm.employee'),
        ),
    ]
