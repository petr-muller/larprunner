# This Python file uses the following encoding: utf-8
from django.db import models

# Create your models here.

class Game(models.Model):
  name          = models.CharField("Jméno", maxlength=30)
  roles_male    = models.PositiveSmallIntegerField("Počet mužských rolí")
  roles_female  = models.PositiveSmallIntegerField("Počet ženských rolí")
  roles_both    = models.PositiveSmallIntegerField("Počet obecných rolí")  
   
  def __str__(self):
    return self.name
