from django import newforms as forms
from models import Game

class SlotForm(forms.Form):
  def __init__(self, slotid, *args, **kwargs):
    super(SlotForm, self).__init__(*args, **kwargs)
    self.fields['games'].choices = [('', '----------')] + [(lang.id, lang.name) for lang in Game.objects.all()]
    self.fields['slot'].widget = forms.HiddenInput()
    self.fields['slot'].initial = slotid
     
  games = forms.ChoiceField()
  slot  = forms.CharField()
  price = forms.IntegerField()
  note  = forms.CharField()