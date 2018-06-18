# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('DRP', '0017_auto_20160501_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='performedreaction',
            name='reference',
            field=models.CharField(max_length=40, validators=[django.core.validators.RegexValidator(
                '[A-Za-z0-9\\._]*[A-Za-z][A-Za-z0-9\\._]*', 'Please include only values which are limited to alphanumeric characters, underscores, periods, and must include at least one alphabetic character.')]),
        ),
    ]
