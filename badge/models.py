from django.db import models

def image_upload_path(instance, filename):
    return f'{"badge"}/{instance.id}/{filename}'

class Badge(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to=image_upload_path, blank=False, null=False)

    def __str__(self) -> str:
        return self.name
    
    