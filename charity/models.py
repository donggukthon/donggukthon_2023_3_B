from django.db import models
# from fishbread.models import Fishbread

# Create your models here.
class Charity(models.Model):
    charity_id = models.IntegerField(primary_key=True)
    # fishbread_id = models.ForeignKey(Fishbread, blank=False, null=False, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    content = models.TextField()
    count = models.IntegerField()