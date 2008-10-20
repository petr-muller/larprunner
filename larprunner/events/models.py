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

  def unregister(self, player):
    registration = Registration.objects.get(player=player, event=self)
    registration.answers.all().delete()
    registration.delete()

    slots = self.multigameslot_set.all()
    for slot in slots:
      for game in slot.gameinslot_set.all():
        SlotGameRegistration.objects.filter(player=player, slot=game).delete()

  def getGamesForPlayer(self, player):
    games = []
    for slot in self.multigameslot_set.all():
      games.append(slot.getGameForPlayer(player))

    while None in games:
      games.remove(None)
    return games

class MultiGameSlot(models.Model):
  name = models.CharField("Název", maxlength=50)
  start = models.DateTimeField("Začátek")
  end = models.DateTimeField("Konec")
  event = models.ForeignKey(Event)
  def __str__(self):
    return self.name

  def printify(self):
    self.games_to_print = GameInSlot.objects.filter(slot = self)
    for game in self.games_to_print:
      game.printify()

  def getGameForPlayer(self, player):
    for game in self.gameinslot_set.all():
      if game.isPlayerRegged(player):
        return game

    return None

class GameInSlot(models.Model):
  game  = models.ForeignKey(Game)
  slot  = models.ForeignKey(MultiGameSlot)
  price = models.PositiveSmallIntegerField("Cena")
  note  = models.CharField("Fancy name", maxlength=256)

  def isPlayerRegged(self, player):
    try:
      self.slotgameregistration_set.get(player=player)
      return True
    except SlotGameRegistration.DoesNotExist:
      return False

  def printify(self):
    self.regs = SlotGameRegistration.objects.filter(slot=self)

  def isFreeFor(self, player_gender):
    regsforme = SlotGameRegistration.objects.filter(slot=self)
    actm=actf=0
    for reg in regsforme:
      if reg.player.gender == "Male":
        actm += 1
      else:
        actf += 1
    if player_gender == "Male":
      return (actm<self.game.getMaxM()) and (actm+actf < self.game.getMaxPlayers())
    else:
      return (actf<self.game.getMaxF()) and (actm+actf < self.game.getMaxPlayers())

class Registration(models.Model):
  player = models.ForeignKey(Player)
  event  = models.ForeignKey(Event)
  answers = models.ManyToManyField(Answer, null=True)

class SlotGameRegistration(models.Model):
  player  = models.ForeignKey(Player)
  slot    = models.ForeignKey(GameInSlot)
  answers = models.ManyToManyField(Answer, null=True)