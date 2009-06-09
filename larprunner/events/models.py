# This Python file uses the following encoding: utf-8

from django.db import models
from larprunner.questions.models import Question, Answer
from larprunner.admin.models import Game
from larprunner.users.models import Player
from django.forms.util import smart_unicode
from django.template.loader import render_to_string
from django.conf import settings

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
  name  = models.CharField("Název", max_length=50)
  type  = models.CharField("Typ", max_length=10, choices=ETYPES) 
  fluff = models.TextField("Fluff")
  start = models.DateTimeField("Začátek")
  end   = models.DateTimeField("Konec")
  game  = models.ForeignKey(Game, null=True)
  state   = models.CharField("Stav", max_length=10, choices=ASTATES, default="CREATED")
  question = models.ManyToManyField(QuestionForEvent, null=True)
  information_url = models.URLField(u"Informace o akci", blank=True)

  def __unicode__(self):
    return unicode(self.name)

  def setTempUrl(self):
    if self.information_url:
      self.tmpurl = self.information_url
    elif self.game:
      self.tmpurl = self.game.getUrl()
    else:
      self.tmpurl = None

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

  def mailToPlayer(self, player):
    from django.core.mail import send_mail
    subject = render_to_string('events/registration_subject.txt',
                              { 'SITE_NAME': settings.SITE_NAME,
                                'event'    : self })
    subject = ''.join(subject.splitlines())
    slots = self.multigameslot_set.all()
    for slot in slots:
      slot.appliedfor = slot.getGameForPlayer(player)

    message = render_to_string('events/registration_mail.txt',
                              { 'SITE_URL'  : settings.SITE_URL,
                                'SITE_NAME' : settings.SITE_NAME,
                                'slots'     : slots,
                                'event'     : self})
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [player.user.email])

class MultiGameSlot(models.Model):
  name = models.CharField("Název", max_length=50)
  start = models.DateTimeField("Začátek")
  end = models.DateTimeField("Konec")
  event = models.ForeignKey(Event)

  def __unicode__(self):
    return unicide(self.name)

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
  note  = models.CharField("Fancy name", max_length=256)

  def asLine(self):
    if self.note != "":
      tmp_note = u", %s" % smart_unicode(self.note)
    else:
      tmp_note = u""
    return u"%s (%s Kč)%s" % (smart_unicode(self.game.name), smart_unicode(self.price), smart_unicode(tmp_note))

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
