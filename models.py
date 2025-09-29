from django.db import models

class UserImage(models.Model):
    image = models.ImageField(upload_to='user_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class ShirtImage(models.Model):
    image = models.ImageField(upload_to='shirt_images/')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Run in Django shell, NOT in models.py
# from shirt_app.models import ShirtImage
# 
# shirt = ShirtImage.objects.get(name="YourShirtName")  # Use the correct shirt name
# shirt.image.name = "shirt_images/InputShirtImg.png"   # Use the correct filename
# shirt.save()
