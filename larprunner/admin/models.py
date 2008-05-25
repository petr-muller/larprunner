from django.db import models

# Create your models here.

class Game(models.Model):
  name = models.CharField(maxlength=30)
  
  def __str__(self):
    return self.name
