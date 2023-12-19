from django.db import models
from charity.models import Charity
from accounts.models import User

def image_upload_path(instance, filename):
    return f'{"fishbread"}/{instance.id}/{filename}'

class FishbreadType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    image1 = models.ImageField(upload_to=image_upload_path, blank=False, null=False)
    image2 = models.ImageField(upload_to=image_upload_path, blank=False, null=False)
    image3 = models.ImageField(upload_to=image_upload_path, blank=False, null=False)

    def __str__(self) -> str:
        return self.name
    
class Fishbread(models.Model):
    id = models.AutoField(primary_key=True)
    charity = models.ManyToManyField(Charity, blank=True)
    price = models.IntegerField(default=0)
    start_day = models.DateField(auto_now_add=True)
    end_day = models.DateField()
    isDonated = models.BooleanField(default=False) # 기부되었는지
    fishbreadtype = models.ForeignKey(FishbreadType, on_delete=models.CASCADE, related_name='fishbread')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fishbreads')

    