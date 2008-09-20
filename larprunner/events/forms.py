from django import newforms as forms
from larprunner.questions.models import Question
from larprunner.admin.models import Game 
from models import Event

class EventForm(forms.Form):  
  id    = forms.IntegerField(widget=forms.HiddenInput, required=False)
  name  = forms.CharField(max_length=50)
  type  = forms.CharField(widget=forms.HiddenInput, max_length=10)
  fluff = forms.CharField(widget=forms.Textarea(attrs={'rows' : 10,
                                                       'cols' : 40}))
  start = forms.DateTimeField()  
  end   = forms.DateTimeField()
  game  = forms.ModelChoiceField(Game.objects.all())  
  
  def loadValues(self, event):    
    self.initial["id"] = event.id
    self.initial["type"] = event.type
    self.initial["name"] = event.name
    self.initial["fluff"] = event.fluff
    self.initial["start"] = event.start
    self.initial["end"] = event.end
    if event.game is not None:
      self.initial["game"] = event.game.id
  
  def save(self,eventid=None):
    if self.clean_data["id"] is None:
      event = Event.objects.create(type =self.clean_data["type"],
                                   name =self.clean_data["name"],
                                   fluff=self.clean_data["fluff"],
                                   end  =self.clean_data["end"],
                                   start=self.clean_data["start"],
                                   game =self.clean_data["game"],
                                   )
    else:
      event = Event.objects.get(id=self.clean_data["id"])
      event.type  = self.clean_data["type"]
      event.name  = self.clean_data["name"]
      event.fluff = self.clean_data["fluff"]
      event.start = self.clean_data["start"]
      event.end   = self.clean_data["end"]
      event.game  = self.clean_data["game"]
    event.save()
  
class SingleEventForm(EventForm):
  type  = forms.CharField(widget=forms.HiddenInput, max_length=10, initial="single")

class MultiEventForm(EventForm):
  type  = forms.CharField(widget=forms.HiddenInput, max_length=10, initial="multi")
  game  = forms.ModelChoiceField(Game.objects.all(), widget=forms.HiddenInput, required=False)

class RegistrationForm(forms.Form):    
  """
  Dynamic form that allows the user to change and then verify the data that was parsed
  """
  def setFields(self, kwds):
    """
    Set the fields in the form
    """
    keys = kwds.keys()
    keys.sort()
    for k in keys:
      self.fields[k] = kwds[k]
            
  def setData(self, kwds):
    """
    Set the data to include in the form
    """
    keys = kwds.keys()
    keys.sort()
    for k in keys:
      self.data[k] = kwds[k]
            
  def validate(self, post):
    """
    Validate the contents of the form
    """
    for name,field in self.fields.items():
      try:
        field.clean(post.get(name, 'off'))
      except forms.ValidationError, e:
        self.errors[name] = e.messages
      
        
  def save(self, eventid):
    event = Event.objects.get(id=eventid)
    event.question.clear()
    for queid in [ int(x) for x in self.data.keys() ]:
      event.question.add(Question.objects.get(id=queid))
