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

class Log(models.Model):
  date = models.DateTimeField(auto_now_add=True)
  user = models.CharField(maxlength=30)
  message = models.TextField()
  def __str__(self):
    return self.message 

class EventOneGame(models.Model):
  name  = models.CharField("Název", maxlength=50)
  fluff = models.TextField("Fluff")
  start = models.DateTimeField("Začátek")
  end   = models.DateTimeField("Konec")
  game  = models.ForeignKey(Game)
  def __str__(self):
    return self.name
  
class EventMultiGame(models.Model):
  name = models.CharField("Název", maxlength=50)
  fluff = models.TextField("Fluff")
  start = models.DateTimeField("Začátek")
  end   = models.DateTimeField("Konec")
  def __str__(self):
    return self.name

class MultiGameSlot(models.Model):
  name = models.CharField("Název", maxlength=50)
  start = models.DateTimeField("Začátek")
  end = models.DateTimeField("Konec")
  event = models.ForeignKey(EventMultiGame)
  def __str__(self):
    return self.name  

class GameInSlot(models.Model):
  game  = models.ForeignKey(Game)
  slot  = models.ForeignKey(MultiGameSlot)
  price = models.PositiveSmallIntegerField("Cena")
  note  = models.CharField("Fancy name", maxlength=256)

