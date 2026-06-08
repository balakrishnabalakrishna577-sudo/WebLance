from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('features', '0003_booking_cancel_reason'),
        ('dashboard', '0004_projectreview'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(
                    choices=[
                        ('design', 'Design'),
                        ('development', 'Development'),
                        ('testing', 'Testing'),
                        ('meeting', 'Meeting / Call'),
                        ('revision', 'Revision'),
                        ('deployment', 'Deployment'),
                        ('other', 'Other'),
                    ],
                    default='development',
                    max_length=20,
                )),
                ('description', models.TextField(blank=True)),
                ('hours', models.DecimalField(decimal_places=2, help_text='Hours worked (e.g. 1.5)', max_digits=6)),
                ('log_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='time_logs',
                    to='dashboard.clientproject',
                )),
                ('logged_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='time_logs',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['-log_date', '-created_at'],
            },
        ),
    ]
