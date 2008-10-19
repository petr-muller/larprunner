# This Python file uses the following encoding: utf-8
from django.db import models
from larprunner.questions.models import Question

# Create your models here.

class Game(models.Model):
  name          = models.CharField("Jméno", maxlength=30)
  roles_male    = models.PositiveSmallIntegerField("Počet mužských rolí")
  roles_female  = models.PositiveSmallIntegerField("Počet ženských rolí")
  roles_both    = models.PositiveSmallIntegerField("Počet obecných rolí")
  def __str__(self):
    return self.name

  def getMaxM(self):
    return self.roles_male + self.roles_both

  def getMaxF(self):
    return self.roles_female + self.roles_both

  def getMaxPlayers(self):
    return self.roles_male + self.roles_female + self.roles_both

class QuestionForGame(models.Model):
  question  = models.ForeignKey(Question)
  required  = models.BooleanField("Vyžadováno")
  game      = models.ForeignKey(Game)

  def asField(self):
    return self.question.asField(self.required)

class Log(models.Model):
  date = models.DateTimeField(auto_now_add=True)
  user = models.CharField(maxlength=30)
  message = models.TextField()
  def __str__(self):
    return self.message 



