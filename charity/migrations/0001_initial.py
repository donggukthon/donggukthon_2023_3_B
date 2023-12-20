# Generated by Django 5.0 on 2023-12-20 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Charity',
            fields=[
                ('charity_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('content', models.TextField()),
                ('count', models.IntegerField()),
            ],
        ),
    ]
