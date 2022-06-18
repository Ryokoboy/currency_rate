from django.db import models


class Order(models.Model):
    id = models.IntegerField(primary_key=True)
    order_num = models.CharField(max_length=10)
    price_USD = models.IntegerField()
    delivery_date = models.CharField(max_length=20)
    price_RUB = models.FloatField()
