from django.db import models

def image_upload_path(instance, filename):
    return f'{"badge"}/{instance.id}/{filename}'

class Badge(models.Model):
    id = models.IntegerField(primary_key=True)
    image1 = models.ImageField(upload_to=image_upload_path, blank=False, null=False)
    image2 = models.ImageField(upload_to=image_upload_path, blank=False, null=False)

    def __str__(self):
        return str(self.id)
    
    