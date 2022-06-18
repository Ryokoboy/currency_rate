# Generated by Django 4.0.5 on 2022-06-18 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('order_num', models.CharField(max_length=10)),
                ('price_USD', models.IntegerField()),
                ('delivery_date', models.CharField(max_length=20)),
                ('price_RUB', models.FloatField()),
            ],
        ),
    ]
