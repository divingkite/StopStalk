# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stalkerNew', '0002_auto_20160217_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='cc',
            field=models.CharField(max_length=20, null=True, verbose_name=b'Codechef handle name', blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='cf',
            field=models.CharField(max_length=20, null=True, verbose_name=b'Codeforces handle name', blank=True),
        ),
    ]
