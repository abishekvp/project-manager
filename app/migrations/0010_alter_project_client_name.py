# Generated by Django 5.1.2 on 2024-11-02 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_project_manager_delete_personaltask'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='client_name',
            field=models.CharField(max_length=64, null=True),
        ),
    ]