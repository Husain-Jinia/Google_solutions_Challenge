# Generated by Django 3.1.7 on 2021-03-30 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Predictor', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='predictions',
            name='id',
        ),
        migrations.AlterField(
            model_name='predictions',
            name='date',
            field=models.CharField(max_length=64, primary_key=True, serialize=False),
        ),
    ]
