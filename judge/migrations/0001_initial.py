# Generated by Django 2.1.7 on 2019-03-19 07:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rest', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Timestamp')),
                ('file', models.FileField(upload_to='tests/', verbose_name='Tests File')),
            ],
            options={
                'verbose_name': 'Test config',
                'verbose_name_plural': 'Test configs',
            },
        ),
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Start time')),
                ('freeze_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Freeze time')),
                ('end_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='End time')),
                ('team', models.BooleanField(default=False, verbose_name='Team contest')),
                ('penalty', models.IntegerField(default=0, verbose_name='Penalty for wrong submissions')),
                ('printing', models.BooleanField(default=False, verbose_name='Is printing avaliable')),
            ],
            options={
                'verbose_name': 'Contest',
                'verbose_name_plural': 'Contests',
                'ordering': ['name'],
                'permissions': (('see_unfrozen_ranking', 'Can see unfrozen ranking'),),
            },
        ),
        migrations.CreateModel(
            name='InputTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Timestamp')),
                ('file', models.FileField(upload_to='tests/', verbose_name='Tests File')),
            ],
            options={
                'verbose_name': 'Test input',
                'verbose_name_plural': 'Test inputs',
            },
        ),
        migrations.CreateModel(
            name='OutputTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Timestamp')),
                ('file', models.FileField(upload_to='tests/', verbose_name='Tests File')),
            ],
            options={
                'verbose_name': 'Test output',
                'verbose_name_plural': 'Test outputs',
            },
        ),
        migrations.CreateModel(
            name='PrintRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Waiting'), (2, 'Printing'), (3, 'Printed')], default=1, verbose_name='Status')),
                ('source', models.TextField(verbose_name='Source code')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Send time')),
                ('language', models.CharField(choices=[('c', 'C'), ('cpp', 'C++'), ('pas', 'Pascal'), ('py', 'Python'), ('java', 'Java'), ('plain', 'Plain')], max_length=10, verbose_name='Language')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='printRequests', to=settings.AUTH_USER_MODEL, verbose_name='Author')),
                ('contest', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='printRequests', to='judge.Contest', verbose_name='Contest')),
            ],
            options={
                'verbose_name': 'Print request',
                'verbose_name_plural': 'Print requests',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codename', models.SlugField(help_text="Example: 'FIB01'. A short text to identify this problem, used as an id for urls.", max_length=10, unique=True, verbose_name='Codename')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('content', models.TextField(default='\n<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.\nCurabitur id tortor at dui porta sollicitudin in sit amet nisi.\nNunc venenatis tincidunt orci eget imperdiet.\nMaecenas rutrum arcu at nunc aliquet pulvinar.\nMaecenas blandit augue nec augue semper id ornare lorem congue.\nEtiam non erat lorem, eget semper eros.</p>\n\n<h3>Input</h3>\nOn the input the program recives two binary numbers.\n\n<h3>Output</h3>\nOn the output the program should print a binary number.\n', verbose_name='Content')),
                ('pdf', models.FileField(blank=True, null=True, upload_to='problems/', verbose_name='PDF')),
            ],
            options={
                'verbose_name': 'Problem',
                'verbose_name_plural': 'Problems',
                'ordering': ['codename'],
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institute_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Institute name')),
                ('team_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Team name')),
                ('room_number', models.CharField(blank=True, max_length=10, null=True, verbose_name='Room number')),
                ('computer_number', models.CharField(blank=True, max_length=10, null=True, verbose_name='Computer number')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
            },
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('returncode', models.IntegerField(default=0, verbose_name='Return code')),
                ('mark', models.BooleanField(default=True, verbose_name='Mark')),
                ('time', models.FloatField(default=0, verbose_name='Execution time')),
            ],
            options={
                'verbose_name': 'Result',
                'verbose_name_plural': 'Results',
                'ordering': ['time'],
            },
        ),
        migrations.CreateModel(
            name='SampleIO',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input', models.TextField(verbose_name='Input')),
                ('output', models.TextField(verbose_name='Output')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.Problem', verbose_name='Problem')),
            ],
            options={
                'verbose_name': 'Sample I/O',
                'verbose_name_plural': 'Sample I/O',
            },
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.TextField(verbose_name='Source code')),
                ('language', models.CharField(choices=[('c', 'C'), ('cpp', 'C++'), ('pas', 'Pascal'), ('py', 'Python'), ('java', 'Java')], max_length=10, verbose_name='Language')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Send time')),
                ('compilelog', models.TextField(blank=True, default='', null=True, verbose_name='Compilation log')),
                ('score', models.IntegerField(default=-1, verbose_name='Score')),
                ('status', models.IntegerField(choices=[(1, 'Waiting'), (2, 'Judging'), (3, 'Judged')], default=1, verbose_name='Status')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to=settings.AUTH_USER_MODEL, verbose_name='Author')),
                ('contest', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='judge.Contest', verbose_name='Contest')),
                ('node', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rest.Node', verbose_name='Node')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='judge.Problem', verbose_name='Problem')),
            ],
            options={
                'verbose_name': 'Submission',
                'verbose_name_plural': 'Submissions',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Tests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('config', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='config', to='judge.ConfigTest', verbose_name='Config')),
                ('input', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='input', to='judge.InputTest', verbose_name='Inputs')),
                ('output', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='output', to='judge.OutputTest', verbose_name='Outputs')),
                ('problem', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='judge.Problem', verbose_name='Problem')),
            ],
            options={
                'verbose_name': 'Tests',
                'verbose_name_plural': 'Tests',
            },
        ),
        migrations.AddField(
            model_name='result',
            name='submission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='judge.Submission', verbose_name='Submission'),
        ),
        migrations.AddField(
            model_name='printrequest',
            name='problem',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='printRequests', to='judge.Problem', verbose_name='Problem'),
        ),
        migrations.AddField(
            model_name='contest',
            name='problems',
            field=models.ManyToManyField(related_name='contests', to='judge.Problem', verbose_name='Problems'),
        ),
    ]
