# This Python file uses the following encoding: utf-8
from django import newforms as forms
from larprunner.questions.models import Question
from larprunner.admin.models import Game 
from models import Event, ASTATES
from larprunner.events.models import Registration
from larprunner.users.models import Player

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

  def setGame(self, gameid):
    return
  
  def save(self,eventid=None):
    if self.data["id"] is None:
      event = Event.objects.create(type =self.data["type"],
                                   name =self.data["name"],
                                   fluff=self.data["fluff"],
                                   end  =self.data["end"],
                                   start=self.data["start"],
                                   game =self.data["game"],
                                   )
    else:
      event = Event.objects.get(id=self.data["id"])
      event.type  = self.data["type"]
      event.name  = self.data["name"]
      event.fluff = self.data["fluff"]
      event.start = self.data["start"]
      event.end   = self.data["end"]
      self.setGame(self.data["game"])
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

class DynamicForm(forms.Form):
  def setFields(self, kwds):
    keys = kwds.keys()
    keys.sort()
    for k in keys:
      self.fields[k] = kwds[k]
            
  def setData(self, kwds):
    keys = kwds.keys()
    keys.sort()
    for k in keys:
      self.data[k] = kwds[k]
            
  def validate(self, post):
    for name,field in self.fields.items():
      try:
        field.clean(post.get(name, 'off'))
      except forms.ValidationError, e:
        self.errors[name] = e.messages
        
class RegistrationForm(DynamicForm):
  def save(self, eventid):
    event = Event.objects.get(id=eventid)
    event.question.clear()
    for queid in [ int(x) for x in self.data.keys() ]:
      event.question.add(Question.objects.get(id=queid))

class ApplicationForm(DynamicForm):
  id = forms.CharField(widget=forms.HiddenInput)
  def save(self, eventid, user):
    if self.data["id"] == "":
      reg = Registration.objects.create(player = Player.objects.get(user=user),
                                      event = Event.objects.get(id=eventid),
                                      )
    return
