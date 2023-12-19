from django.db import models
from charity.models import Charity

# Create your models here.
class Fishbread(models.Model):
    id = models.AutoField(primary_key=True)
    charity = models.ManyToManyField(Charity, blank=True)
    name = models.CharField(max_length=20)
    price = models.IntegerField(default=0)
    day = models.IntegerField(default=0)
    isDonated = models.BooleanField(default=False) # 기부되었는지ㅈ