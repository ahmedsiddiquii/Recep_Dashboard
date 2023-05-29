# Generated by Django 4.2.1 on 2023-05-08 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tool', '0003_delete_leads'),
    ]

    operations = [
        migrations.CreateModel(
            name='Leads',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=100)),
                ('last_name', models.CharField(default=None, max_length=100)),
                ('first_name', models.CharField(default=None, max_length=100)),
                ('title', models.CharField(default=None, max_length=100, null=True)),
                ('email', models.CharField(default=None, max_length=100, null=True)),
                ('phone_number', models.CharField(default=None, max_length=100, null=True)),
                ('linkedin', models.CharField(default=None, max_length=400, null=True)),
                ('employees', models.CharField(default=None, max_length=100, null=True)),
                ('company_website', models.CharField(default=None, max_length=100, null=True)),
                ('company_name', models.CharField(default=None, max_length=100, null=True)),
                ('location', models.CharField(default=None, max_length=100, null=True)),
                ('linkedin_sales_navigator', models.CharField(default=None, max_length=500, null=True)),
            ],
        ),
    ]