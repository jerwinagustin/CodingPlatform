# Generated migration for Submission model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('professors', '0002_activity'),
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.TextField(help_text="Student's submitted code")),
                ('language', models.CharField(default='python', max_length=50)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('result', models.CharField(choices=[('pass', 'Pass'), ('fail', 'Fail'), ('error', 'Error'), ('timeout', 'Timeout'), ('pending', 'Pending')], default='pending', max_length=20)),
                ('score', models.IntegerField(default=0, help_text='Score out of 100')),
                ('test_results', models.JSONField(default=list, help_text='Detailed results for each test case')),
                ('output', models.TextField(blank=True, help_text='Actual output from execution')),
                ('error_message', models.TextField(blank=True, help_text='Error message if any')),
                ('execution_time', models.FloatField(blank=True, help_text='Execution time in seconds', null=True)),
                ('memory_used', models.IntegerField(blank=True, help_text='Memory used in KB', null=True)),
                ('celery_task_id', models.CharField(blank=True, help_text='Celery task ID for tracking', max_length=100)),
                ('is_final', models.BooleanField(default=False, help_text='True for submit, False for run/test')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='professors.activity')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='students.student')),
            ],
            options={
                'db_table': 'submissions',
                'ordering': ['-created_at'],
            },
        ),
    ]
