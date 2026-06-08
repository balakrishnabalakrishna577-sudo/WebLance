import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notif_type', models.CharField(
                    choices=[
                        ('project_update', 'Project Update'),
                        ('milestone',      'Milestone'),
                        ('message',        'Message'),
                        ('invoice',        'Invoice'),
                        ('booking',        'Booking'),
                        ('agreement',      'Agreement'),
                        ('quote',          'Quote Request'),
                        ('review',         'Review'),
                        ('system',         'System'),
                    ],
                    default='system',
                    max_length=30,
                )),
                ('title',      models.CharField(max_length=200)),
                ('message',    models.TextField(blank=True)),
                ('url',        models.CharField(blank=True, help_text='Link to navigate to on click', max_length=500)),
                ('is_read',    models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('recipient',  models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='notifications',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['recipient', 'is_read'], name='notif_recip_read_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['recipient', 'created_at'], name='notif_recip_time_idx'),
        ),
    ]
