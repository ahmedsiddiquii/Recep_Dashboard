# Generated by Django 4.2.1 on 2023-05-27 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tool', '0006_job'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='location',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
