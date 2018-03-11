# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-11 21:55
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(blank=True, default='Game', max_length=255)),
                ('board', models.TextField(blank=True, default='', help_text='Board as a JSON matrix. (0-9: adjacent mines, x: mine)')),
                ('player_board', models.TextField(blank=True, default='', help_text='Board as a JSON matrix. (v: visible, h: hidden, ?: question mark, !: exclamation mark.')),
                ('state', models.IntegerField(choices=[(0, 'new'), (1, 'started'), (2, 'paused'), (3, 'timeout'), (4, 'won'), (5, 'lost')], default=0)),
                ('duration_seconds', models.IntegerField(default=90, help_text='Game duration: 90 seconds')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('created',),
                'verbose_name': 'Game',
                'verbose_name_plural': 'Games',
            },
        ),
    ]
