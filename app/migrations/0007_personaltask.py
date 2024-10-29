# Generated by Django 4.2.6 on 2024-10-29 18:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("app", "0006_permisison_reason"),
    ]

    operations = [
        migrations.CreateModel(
            name="PersonalTask",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=64)),
                ("description", models.TextField()),
                ("status", models.CharField(default="TODO", max_length=10)),
                ("correction", models.TextField(null=True)),
                ("discussion", models.TextField(null=True)),
                ("reason", models.TextField(null=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("started", models.DateTimeField(null=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("due", models.DateField(null=True)),
                (
                    "assigned_to",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
