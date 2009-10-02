# This Python file uses the following encoding: utf-8

from django.db import models
from larprunner.questions.models import Question, Answer
from larprunner.admin.models import Game
from larprunner.users.models import Player
from django.forms.util import smart_unicode
from django.template.loader import render_to_string
from django.conf import settings
from larprunner.hub.models import Hub

# Create your models here.
ASTATES=(
           ('CREATED' , 'Vytvořená'),
           ('OPEN'    , 'Otevřená'),
           ('CLOSED'  , 'Zavřená'),
           ('ARCHIVED', 'Archivovaná'),
        )

DSTATES=dict(ASTATES)
DSTATES['NONE']="--nic--"

ACTIONS=(  ('NONE'    , "--nic--"),
           ('CREATED' , 'Nastavit jako "Vytvořená"'),
           ('OPEN'    , 'Otevřít registrace'),
           ('CLOSED'  , 'Uzavřít registrace'),
           ('ARCHIVED', 'Archivovat'),
        )

DACTIONS=dict(ACTIONS)

STATE_NEXT={
    "CREATED":"OPEN",
    "OPEN":"CLOSED",
    "CLOSED":"ARCHIVED",
    "ARCHIVED":"NONE"
    }

STATE_PREV={
    "CREATED":"NONE",
    "OPEN":"CREATED",
    "CLOSED":"OPEN",
    "ARCHIVED":"CLOSED"
    }

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
  admins = models.CharField("Název", max_length=1000, blank=True)

  def getAdminRecipients(self):
    if self.admins == "":
      return None
    return self.admins.split(";")

  def getName(self):
    return self.name

  def state_previous(self):
    return STATE_PREV[self.state]

  def state_next(self):
    return STATE_NEXT[self.state]

  def state_previous_name(self):
    return DSTATES[self.state_previous()]

  def state_next_name(self):
    return DSTATES[self.state_next()]

  def state_name(self):
    return DSTATES[self.state]

  def action_previous(self):
    return DACTIONS[self.state_previous()]

  def action_next(self):
    return DACTIONS[self.state_next()]

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

    Hub().deliver("player has unsubscribed from event",
                  {"player": player.getFullName(),  "event": self } )

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

  def getPlayers(self):
    regs = Registration.objects.filter(event=self).order_by(u"player")
    people = [ reg.player for reg in regs ]
    return people

  def getPeopleTable(self, qfe=True, qfg=True, slotted=False, sorted="surname"):
    players = []
    headlines = []
    slots=[]
    headlines.extend(self.getQuestionNames(qfe, qfg))
    if slotted and self.type == "multi":
      slots = MultiGameSlot.objects.filter(event=self)
      headlines.extend([ slot.getName() for slot in slots ])

    for player in self.getPlayers():
      reg   = Registration.objects.get(player=player, event=self)
      record = []
      record.append(player)
      record.append(reg.created)
      if qfg and self.game:
        row = []
        for question in [ que.question for que in self.game.questionforgame_set.all()]:
          answers = reg.answers.filter(question=question)
          row.extend([ u",".join( [ ans.answer for ans in answers ]) ])
        record.append(row)
      else:
        record.append(None)
      if qfe:
        row = []
        for question in [ que.question for que in self.question.all()]:
          answers = reg.answers.filter(question=question)
          row.extend([ u",".join( [ ans.answer for ans in answers ]) ])
        record.append(row)
      else:
        record.append(None)

      if slots:
        row = []
        for slot in slots:
          game = slot.getGameForPlayer(player)
          if game:
            row.append(game.getGameName())
          else:
            row.append("--nic---")
      else:
        row = None
      record.append(row)
      players.append(record)

    if sorted == "surname":
      players.sort(lambda x,y: cmp(x[0].surname.lower(), y[0].surname.lower()))
    elif sorted == "created":
      players.sort(lambda x,y: cmp(x[1], y[1]))

    return players, headlines

  def getQuestionNames(self, qfg=True, qfe=True):
    headlines = []
    if self.game is not None and qfg:
      headlines.extend([ que.question.getCaption() for que in self.game.questionforgame_set.all() ])
    if qfe:
      headlines.extend ([ que.question.getCaption() for que in self.question.all() ])
    return headlines

class MultiGameSlot(models.Model):
  name = models.CharField("Název", max_length=50)
  start = models.DateTimeField("Začátek")
  end = models.DateTimeField("Konec")
  event = models.ForeignKey(Event)

  def __unicode__(self):
    return unicode(self.name)

  def printify(self):
    self.games_to_print = GameInSlot.objects.filter(slot = self)
    for game in self.games_to_print:
      game.printify()

  def getGameForPlayer(self, player):
    for game in self.gameinslot_set.all():
      if game.isPlayerRegged(player):
        return game

    return None

  def getName(self):
    return "Slot '%s'" % self.name

class GameInSlot(models.Model):
  game  = models.ForeignKey(Game)
  slot  = models.ForeignKey(MultiGameSlot)
  price = models.PositiveSmallIntegerField("Cena")
  note  = models.CharField("Fancy name", max_length=256)

  def getGameName(self):
    return self.game.getName()

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
  created = models.DateTimeField("Created", auto_now_add=True);
  answers = models.ManyToManyField(Answer, null=True)

class SlotGameRegistration(models.Model):
  player  = models.ForeignKey(Player)
  slot    = models.ForeignKey(GameInSlot)
  created = models.DateTimeField("Created", auto_now_add=True);
  answers = models.ManyToManyField(Answer, null=True)
