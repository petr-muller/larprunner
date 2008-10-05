# This Python file uses the following encoding: utf-8
from django import newforms as forms
from larprunner.questions.models import Question, ChoicesForQuestion
from larprunner.admin.models import Game 
from models import Event, ASTATES
from larprunner.events.models import Registration, QuestionForEvent, SlotGameRegistration, GameInSlot
from larprunner.users.models import Player
from larprunner.events.widgets import RadioSelectWithDisable
from django.db.models import Q

class EventForm(forms.Form):  
  id    = forms.IntegerField(widget=forms.HiddenInput, required=False)
  name  = forms.CharField(max_length=50)
  type  = forms.CharField(widget=forms.HiddenInput, max_length=10)
  fluff = forms.CharField(widget=forms.Textarea(attrs={'rows' : 10,
                                                       'cols' : 40}))
  start = forms.DateTimeField()  
  end   = forms.DateTimeField()
  game  = forms.ModelChoiceField(Game.objects.all(), required=True)
  state = forms.ChoiceField(choices=ASTATES)
  
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
                                   state = self.data["state"]
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

class DynamicForm(forms.Form):
  def setFields(self, kwds):
    keys = kwds.keys()
    keys.sort()
    for k in keys:
      self.fields[k] = kwds[k]

  def setData(self, kwds):
    for name,field in self.fields.items():
        self.data[name] = field.widget.value_from_datadict(
                            kwds, self.add_prefix(name))
    self.is_bound = True

  def validate(self, post):
    self.full_clean()

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

    for key in self.clean_data.keys():
      question = Question.objects.get(id=key)
      choices = ChoicesForQuestion.objects.filter(question=question)
      if len(choices) != 0:
        if [].__class__ != self.clean_data[key].__class__:
          self.clean_data[key] = [self.clean_data[key]]
        for data in self.clean_data[key]:
          reg.answers.create(question=question,
                             answer=str(ChoicesForQuestion.objects.get(id=data).choice))
      else:
        reg.answers.create(question=question,
                           answer = u'%s' % self.clean_data[key])

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
      for game in slot.gameinslot_set.all():
        if game.isFreeFor(player.gender):
          choices.append([game.id, game.game.name])
        else:
          choices.append([game.id, game.game.name, "disabled"])
      fields["%s" % slot.id] = forms.ChoiceField(widget=RadioSelectWithDisable,
                                                 required=False,
                                                 label=slot.name,
                                                 choices=choices)
    self.setFields(fields)

  def save(self, event, user):
    player = Player.objects.get(user=user)
    q = Q()
    for slot in event.multigameslot_set.all():
      for game in slot.gameinslot_set.all():
        q = q | Q(slot=game)
    regs = SlotGameRegistration.objects.filter(q)
    regs = regs.filter(player=player)
    regs.delete()

    for key in self.clean_data.keys():
      if self.clean_data[key] != "":
        sgr = SlotGameRegistration.objects.create(player=player,
                                                  slot=GameInSlot(id=self.clean_data[key]))
        sgr.save()
