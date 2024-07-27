from django.db import models

class Product(models.Model):
    product_id = models.CharField(max_length=100, unique=True)
    average_rating = models.FloatField()
    rating_count = models.IntegerField()

    def __str__(self):
        return self.product_id
