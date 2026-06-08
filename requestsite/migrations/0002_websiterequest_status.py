from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requestsite', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='websiterequest',
            name='status',
            field=models.CharField(
                choices=[('new', 'New'), ('received', 'Received'), ('in_progress', 'In Progress'), ('completed', 'Completed')],
                default='new',
                max_length=20,
            ),
        ),
    ]
