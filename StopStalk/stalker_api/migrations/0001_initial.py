# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contestId', models.IntegerField(null=True)),
                ('name', models.CharField(max_length=30)),
                ('site', models.CharField(max_length=2, choices=[(b'CC', b'Codechef'), (b'CF', b'Codeforces')])),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name=b'Full Name of the Person Whose handle names are stored')),
                ('cc', models.CharField(max_length=20, null=True, verbose_name=b'Codechef handle name', blank=True)),
                ('cf', models.CharField(max_length=20, null=True, verbose_name=b'Codeforces handle name', blank=True)),
                ('owner', models.ForeignKey(related_name='Person', verbose_name=b'User object to which this Person is associated', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PracticeProb',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('index', models.CharField(max_length=2)),
                ('link', models.CharField(max_length=50, verbose_name=b'link of the question')),
                ('site', models.CharField(max_length=2, choices=[(b'CC', b'Codechef'), (b'CF', b'Codeforces')])),
                ('person', models.ForeignKey(to='stalker_api.Person')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('link', models.CharField(max_length=50, verbose_name=b'link of the question')),
                ('site', models.CharField(max_length=2, choices=[(b'CC', b'Codechef'), (b'CF', b'Codeforces')])),
                ('index', models.CharField(max_length=2)),
                ('contest', models.ForeignKey(to='stalker_api.Contest')),
                ('person', models.ForeignKey(to='stalker_api.Person')),
            ],
        ),
        migrations.AddField(
            model_name='contest',
            name='questions',
            field=models.ManyToManyField(to='stalker_api.Person', through='stalker_api.Question'),
        ),
    ]
