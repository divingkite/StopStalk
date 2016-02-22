# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stalkerNew', '0003_auto_20160217_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='contestId',
            field=models.IntegerField(null=True),
        ),
    ]
