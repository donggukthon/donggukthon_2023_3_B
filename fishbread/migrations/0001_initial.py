# Generated by Django 5.0 on 2023-12-20 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('charity', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fishbread',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('price', models.IntegerField(default=0)),
                ('day', models.IntegerField(default=0)),
                ('isDonated', models.BooleanField(default=False)),
                ('charity', models.ManyToManyField(blank=True, to='charity.charity')),
            ],
        ),
    ]
