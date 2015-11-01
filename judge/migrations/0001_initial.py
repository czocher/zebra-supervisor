# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rest', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigTest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Timestamp')),
                ('file', models.FileField(upload_to=b'tests/', verbose_name='Tests File')),
            ],
            options={
                'verbose_name': 'Test config',
                'verbose_name_plural': 'Test configs',
            },
        ),
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Start time')),
                ('freeze_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Freeze time')),
                ('end_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='End time')),
                ('team', models.BooleanField(default=False, verbose_name='Team contest')),
                ('penalty', models.IntegerField(default=0, verbose_name='Penalty for wrong submissions')),
                ('printing', models.BooleanField(default=False, verbose_name='Is printing avaliable')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Contest',
                'verbose_name_plural': 'Contests',
                'permissions': (('view_contest', 'Can view Contest'), ('see_unfrozen_ranking', 'Can see unfrozen ranking')),
            },
        ),
        migrations.CreateModel(
            name='InputTest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Timestamp')),
                ('file', models.FileField(upload_to=b'tests/', verbose_name='Tests File')),
            ],
            options={
                'verbose_name': 'Test input',
                'verbose_name_plural': 'Test inputs',
            },
        ),
        migrations.CreateModel(
            name='OutputTest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Timestamp')),
                ('file', models.FileField(upload_to=b'tests/', verbose_name='Tests File')),
            ],
            options={
                'verbose_name': 'Test output',
                'verbose_name_plural': 'Test outputs',
            },
        ),
        migrations.CreateModel(
            name='PrintRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, verbose_name='Status', choices=[(1, 'Waiting'), (2, 'Printing'), (3, 'Printed')])),
                ('source', models.TextField(verbose_name='Source code')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Send time')),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'c', b'C'), (b'cpp', b'C++'), (b'pas', b'Pascal'), (b'py', b'Python'), (b'java', b'Java'), (b'plain', b'Plain')])),
                ('author', models.ForeignKey(related_name='printRequests', verbose_name='Author', to=settings.AUTH_USER_MODEL)),
                ('contest', models.ForeignKey(related_name='printRequests', verbose_name='Contest', blank=True, to='judge.Contest', null=True)),
            ],
            options={
                'ordering': ['-timestamp'],
                'verbose_name': 'Print request',
                'verbose_name_plural': 'Print requests',
            },
        ),
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codename', models.SlugField(help_text="Example: 'FIB01'. A short text to identify this problem, used as an id for urls.", unique=True, max_length=10, verbose_name='Codename')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('content', models.TextField(default=b'\n<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.\nCurabitur id tortor at dui porta sollicitudin in sit amet nisi.\nNunc venenatis tincidunt orci eget imperdiet.\nMaecenas rutrum arcu at nunc aliquet pulvinar.\nMaecenas blandit augue nec augue semper id ornare lorem congue.\nEtiam non erat lorem, eget semper eros.</p>\n\n<h3>Input</h3>\nOn the input the program recives two binary numbers.\n\n<h3>Output</h3>\nOn the output the program should print a binary number.\n', verbose_name='Content')),
                ('pdf', models.FileField(upload_to=b'problems/', null=True, verbose_name='PDF', blank=True)),
            ],
            options={
                'ordering': ['codename'],
                'verbose_name': 'Problem',
                'verbose_name_plural': 'Problems',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('institute_name', models.CharField(max_length=255, null=True, verbose_name='Institute name', blank=True)),
                ('room_number', models.CharField(max_length=10, null=True, verbose_name='Room number', blank=True)),
                ('computer_number', models.CharField(max_length=10, null=True, verbose_name='Computer number', blank=True)),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
            },
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('returncode', models.IntegerField(default=0, verbose_name='Return code')),
                ('mark', models.BooleanField(default=True, verbose_name='Mark')),
                ('time', models.FloatField(default=0, verbose_name='Execution time')),
            ],
            options={
                'ordering': ['time'],
                'verbose_name': 'Result',
                'verbose_name_plural': 'Results',
            },
        ),
        migrations.CreateModel(
            name='SampleIO',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('input', models.TextField(verbose_name='Input')),
                ('output', models.TextField(verbose_name='Output')),
                ('problem', models.ForeignKey(verbose_name='Problem', to='judge.Problem')),
            ],
            options={
                'verbose_name': 'Sample I/O',
                'verbose_name_plural': 'Sample I/O',
            },
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', models.TextField(verbose_name='Source code')),
                ('language', models.CharField(max_length=10, verbose_name='Language', choices=[(b'c', b'C'), (b'cpp', b'C++'), (b'pas', b'Pascal'), (b'py', b'Python'), (b'java', b'Java')])),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Send time')),
                ('compilelog', models.TextField(default=b'', null=True, verbose_name='Compilation log', blank=True)),
                ('score', models.IntegerField(default=-1, verbose_name='Score')),
                ('status', models.IntegerField(default=1, verbose_name='Status', choices=[(1, 'Waiting'), (2, 'Judging'), (3, 'Judged')])),
                ('author', models.ForeignKey(related_name='submissions', verbose_name='Author', to=settings.AUTH_USER_MODEL)),
                ('contest', models.ForeignKey(related_name='submissions', verbose_name='Contest', blank=True, to='judge.Contest', null=True)),
                ('node', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Node', blank=True, to='rest.Node', null=True)),
                ('problem', models.ForeignKey(related_name='submissions', verbose_name='Problem', to='judge.Problem')),
            ],
            options={
                'ordering': ['-timestamp'],
                'verbose_name': 'Submission',
                'verbose_name_plural': 'Submissions',
            },
        ),
        migrations.CreateModel(
            name='Tests',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('config', models.OneToOneField(related_name='config', verbose_name='Config', to='judge.ConfigTest')),
                ('input', models.OneToOneField(related_name='input', verbose_name='Inputs', to='judge.InputTest')),
                ('output', models.OneToOneField(related_name='output', verbose_name='Outputs', to='judge.OutputTest')),
                ('problem', models.OneToOneField(verbose_name='Problem', to='judge.Problem')),
            ],
            options={
                'verbose_name': 'Tests',
                'verbose_name_plural': 'Tests',
            },
        ),
        migrations.AddField(
            model_name='result',
            name='submission',
            field=models.ForeignKey(related_name='results', verbose_name='Submission', to='judge.Submission'),
        ),
        migrations.AddField(
            model_name='printrequest',
            name='problem',
            field=models.ForeignKey(related_name='printRequests', verbose_name='Problem', blank=True, to='judge.Problem', null=True),
        ),
        migrations.AddField(
            model_name='contest',
            name='problems',
            field=models.ManyToManyField(related_name='contests', verbose_name='Problems', to='judge.Problem'),
        ),
    ]
