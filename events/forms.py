# This Python file uses the following encoding: utf-8
from django import forms
from larprunner.questions.models import Question, ChoicesForQuestion
from larprunner.admin.models import Game 
from models import Event, ASTATES
from larprunner.events.models import Registration, QuestionForEvent, SlotGameRegistration, GameInSlot, MultiGameSlot
from larprunner.users.models import Player
from larprunner.events.widgets import RadioSelectWithDisable
from django.db.models import Q
from django.forms.util import smart_unicode

class EventForm(forms.Form):  
  id    = forms.IntegerField(widget=forms.HiddenInput, required=False)
  name  = forms.CharField(max_length=50, label=u"Název")
  type  = forms.CharField(widget=forms.HiddenInput, max_length=10, label=u"Typ")
  fluff = forms.CharField(widget=forms.Textarea(attrs={'rows' : 10,
                                                       'cols' : 40}),
                          label=u"Popis")
  start = forms.DateTimeField(label=u'Začátek')
  end   = forms.DateTimeField(label=u'Konec')
  game  = forms.ModelChoiceField(Game.objects.all(), required=True, label=u'Hra')
  state = forms.ChoiceField(choices=ASTATES, label=u'Stav')
  url   = forms.URLField(label=u'Informace o akci', verify_exists=True)
  admins = forms.CharField(max_length=1000, label=u"Administrátoři")

  def loadValues(self, event):    
    self.initial["id"] = event.id
    self.initial["type"] = event.type
    self.initial["name"] = event.name
    self.initial["fluff"] = event.fluff
    self.initial["start"] = event.start
    self.initial["end"] = event.end
    if event.game is not None:
      self.initial["game"] = event.game.id
    self.initial["state"] = event.state
    self.initial["url"] = event.information_url
    self.initial["admins"] = event.admins

  def getGame(self, id):
    return Game.objects.get(id=self.data["game"])

  def save(self,eventid=None):
    if not self.data["id"]:
      event = Event.objects.create(type =self.data["type"],
                                   name =self.data["name"],
                                   fluff=self.data["fluff"],
                                   end  =self.data["end"],
                                   start=self.data["start"],
                                   game=self.getGame(self.data["game"]),
                                   state = self.data["state"],
                                   information_url = self.data["url"],
                                   admins = self.data["admins"]
                                   )
    else:
      event = Event.objects.get(id=self.data["id"])
      event.type  = self.data["type"]
      event.name  = self.data["name"]
      event.fluff = self.data["fluff"]
      event.start = self.data["start"]
      event.end   = self.data["end"]
      event.game=self.getGame(self.data["game"])
      event.state = self.data["state"]
      event.information_url = self.data["url"]
      event.admins = self.data["admins"]
    event.save()

  def validate(self):
    return

class SingleEventForm(EventForm):
  type  = forms.CharField(widget=forms.HiddenInput, max_length=10, initial="single")

  def setGame(self, gameid):
    self.game = Game.objects.get(id=gameid)

class MultiEventForm(EventForm):
  type  = forms.CharField(widget=forms.HiddenInput, max_length=10, initial="multi")
  game  = forms.ModelChoiceField(Game.objects.all(), widget=forms.HiddenInput, required=False)

  def setGame(self, gameid):
    return

  def getGame(self, gameid):
    return None
#============================================================
# WARNING: this is dangerous crap
# I don't know a shit how this worked and works, not to speak about fixing it :(
class DynamicForm(forms.Form):
  def setFields(self, kwds):
    keys = kwds.keys()
    keys.sort()
    for k in keys:
      self.fields[k] = kwds[k]

  def setData(self, kwds):
    for name,field in self.fields.items():
        self.data[name] = field.widget.value_from_datadict(
                            kwds, None, self.add_prefix(name))
# seems this ugly hack works. haha. 
# MAJOR MAJOR MAJOR TODO: 
# http://www.b-list.org/weblog/2008/nov/09/dynamic-forms/
# There shalt be your enlightenment

    self.is_bound = True

  def validate(self, post):
    self.full_clean()
#============================================================

class RegistrationForm(DynamicForm):
  def save(self, eventid):
    event = Event.objects.get(id=eventid)
    event.question.all().delete()
    event.question.clear()

    keys = self.data.keys()
    act_keys = []
    for key in keys:
      if key.find("required") == -1:
        act_keys.append(key)
    for queid in act_keys:
      if self.data[queid]:

        quevent = QuestionForEvent.objects.create(question=Question.objects.get(id=queid),
                                                   required=False)
        if self.data["%s_required" % queid]:
          quevent.required = True
        quevent.save()
        event.question.add(quevent)

class ApplicationForm(DynamicForm):
  def save(self, eventid, user):
    reg = Registration.objects.create(player = Player.objects.get(user=user),
                                      event = Event.objects.get(id=eventid))

    for key in self.cleaned_data.keys():
      question = Question.objects.get(id=key)
      choices = ChoicesForQuestion.objects.filter(question=question).order_by("id")
      if len(choices) != 0:
        if [].__class__ != self.cleaned_data[key].__class__:
          self.cleaned_data[key] = [self.cleaned_data[key]]
        for data in self.cleaned_data[key]:
          reg.answers.create(question=question,
                             answer=ChoicesForQuestion.objects.get(id=data).choice)
      else:
        reg.answers.create(question=question,
                           answer = u'%s' % self.cleaned_data[key])

class QuestionsForGamesForm(DynamicForm):
  def save(self, user):
    slots = {}
    for key in self.cleaned_data.keys():
      slotid, question  = key.split('_')
      answer          = self.cleaned_data[key]
      if not slots.has_key(slotid):
        slots[slotid] = []
      slots[slotid].append([question, answer])
    player = Player.objects.get(user=user)
    for slot in slots.keys():
      slot_object   = GameInSlot.objects.get(id=slot)
      registration  = SlotGameRegistration.objects.get(slot=slot_object, player=player)
      registration.answers.clear()
      
      for ans in slots[slot]:
        question = Question.objects.get(id=ans[0])
        choices = ChoicesForQuestion.objects.filter(question=question).order_by("id")
        if len(choices) != 0:
          if ans[1].__class__ != [].__class__ and ans[1].__class__ != ().__class__:
            ans[1] = [ans[1]]
          for data in ans[1]:
            registration.answers.create(question=question,
                                        answer=str(ChoicesForQuestion.objects.get(id=data).choice))
        else:
          registration.answers.create(question=question,
                                      answer = u'%s' % ans[1])

class SlotAppForm(DynamicForm):
  def validate(self):
    for field in self.fields.keys():
      for choice in self.fields[field].choices:
        if len(choice) > 2:
          index = self.fields[field].choices.index(choice)
          self.fields[field].choices[index] = choice[:2]
    self.full_clean()

  def loadFromEvent(self, event, player):
    fields = {}
    for slot in event.multigameslot_set.all():
      choices = []
      initial = -1
      for game in slot.gameinslot_set.all():
        if game.isFreeFor(player.gender):
          choices.append([game.id, game.asLine() ]  )
        else:
          choices.append([game.id, game.asLine(), u"disabled"])
        if SlotGameRegistration.objects.filter(player=player, slot=game).count() > 0:
          initial = game.id

      choices.append([-1, "Nic"])

      fields[u"%s" % slot.id] = forms.ChoiceField(widget=RadioSelectWithDisable,
                                                 required=False,
                                                 label=slot.name,
                                                 choices=choices,
                                                 initial=initial)
    self.setFields(fields)

  def save(self, event, user):
    player = Player.objects.get(user=user)
    for key in self.cleaned_data.keys():
      if self.cleaned_data[key] != u"":
        for reg in MultiGameSlot.objects.get(id=key).gameinslot_set.all():
          reg.slotgameregistration_set.filter(player=player).delete()
        if self.cleaned_data[key] != "-1":
          slot = GameInSlot.objects.get(id=self.cleaned_data[key])
          if slot.isFreeFor(player.gender):
            sgr = SlotGameRegistration.objects.create(player=player, slot=slot)
          else:
            return False
          sgr.save()
    return True
