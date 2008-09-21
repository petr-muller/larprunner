# This Python file uses the following encoding: utf-8

from django.db import models
from larprunner.questions.models import Question, Answer
from larprunner.admin.models import Game
from larprunner.users.models import Player

# Create your models here.
ASTATES=(
           ('CREATED', 'Vytvořená'),
           ('OPEN'   , 'Otevřená'),
           ('CLOSED' , 'Zavřená'),
        )

ETYPES=(
        ('single' , 'Jednoduchá'),
        ('multi'  , 'Vícenásobná')
       )

class QuestionForEvent(models.Model):
  question = models.ForeignKey(Question)
  required = models.BooleanField("Vyžadováno")

  def asField(self):
    return self.question.asField(self.required)

class Event(models.Model):
  name  = models.CharField("Název", maxlength=50)
  type  = models.CharField("Typ", maxlength=10, choices=ETYPES) 
  fluff = models.TextField("Fluff")
  start = models.DateTimeField("Začátek")
  end   = models.DateTimeField("Konec")
  game  = models.ForeignKey(Game, null=True)
  state   = models.CharField("Stav", maxlength=10, choices=ASTATES, default="CREATED")
  question = models.ManyToManyField(QuestionForEvent, null=True)
  def __str__(self):
    return self.name

  def check_free_place(self,player_gender):
    if self.game:
      regsforme = Registration.objects.filter(event=self)
      actm=actf=0
      for reg in regsforme:
        if reg.player.gender == "Male":
          actm += 1
        else:
          actf += 1
      if player_gender == "Male":
        self.free = (actm<self.game.getMaxM()) and (actm+actf < self.game.getMaxPlayers())
      else:
        self.free = (actf<self.game.getMaxF()) and (actm+actf < self.game.getMaxPlayers())
    else:
      self.free = True

  def check_regged(self, player):
    try:
      Registration.objects.get(event=self,
                               player=player)
      self.regged = True
    except Registration.DoesNotExist:
      self.regged = False

class MultiGameSlot(models.Model):
  name = models.CharField("Název", maxlength=50)
  start = models.DateTimeField("Začátek")
  end = models.DateTimeField("Konec")
  event = models.ForeignKey(Event)
  def __str__(self):
    return self.name  

class GameInSlot(models.Model):
  game  = models.ForeignKey(Game)
  slot  = models.ForeignKey(MultiGameSlot)
  price = models.PositiveSmallIntegerField("Cena")
  note  = models.CharField("Fancy name", maxlength=256)

class Registration(models.Model):
  player = models.ForeignKey(Player)
  event  = models.ForeignKey(Event)
  answers = models.ManyToManyField(Answer, null=True)