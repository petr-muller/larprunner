# This Python file uses the following encoding: utf-8
from django.db import models
from larprunner.questions.models import Question

# Create your models here.

class Game(models.Model):
  name          = models.CharField(u"Jméno", max_length=30)
  roles_male    = models.PositiveSmallIntegerField(u"Počet mužských rolí")
  roles_female  = models.PositiveSmallIntegerField(u"Počet ženských rolí")
  roles_both    = models.PositiveSmallIntegerField(u"Počet obecných rolí")
  information_url = models.URLField(u"Informace o hře", blank=True)

  def getUrl(self):
    if self.information_url:
      return self.information_url
    return None

  def __unicode__(self):
    return unicode(self.name)

  def getMaxM(self):
    return self.roles_male + self.roles_both

  def getMaxF(self):
    return self.roles_female + self.roles_both

  def getMaxPlayers(self):
    return self.roles_male + self.roles_female + self.roles_both

class QuestionForGame(models.Model):
  question  = models.ForeignKey(Question)
  required  = models.BooleanField(u"Vyžadováno")
  game      = models.ForeignKey(Game)

  def asField(self):
    return self.question.asField(self.required)

class Log(models.Model):
  date = models.DateTimeField(auto_now_add=True)
  user = models.CharField(max_length=30)
  message = models.TextField()
  def __unicode__(self):
    return unicode(self.message)



