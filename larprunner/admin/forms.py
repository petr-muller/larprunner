# encoding: utf-8
from django import newforms as forms
from models import Game, QuestionForGame
from larprunner.events.forms import DynamicForm
from larprunner.questions.models import Question

class SlotForm(forms.Form):
  def __init__(self, slotid, *args, **kwargs):
    super(SlotForm, self).__init__(*args, **kwargs)
    self.fields['games'].choices = [('', '----------')] + [(lang.id, lang.name) for lang in Game.objects.all()]
    self.fields['slot'].widget = forms.HiddenInput()
    self.fields['slot'].initial = slotid
     
  games = forms.ChoiceField()
  slot  = forms.CharField()
  price = forms.IntegerField()
  note  = forms.CharField(required=False)

class ThrowOutForm(DynamicForm):
  mail = forms.CharField(widget=forms.Textarea)
  def load(self, sgrs):
    for reg in sgrs:
      self.fields["sr%s" % reg.id] = forms.BooleanField(widget=forms.CheckboxInput,
                                                        label=u"Hráč %s, slot %s, hra %s" % (reg.player.name + " " + reg.player.surname,
                                                                                             reg.slot.slot.name,
                                                                                             reg.slot.game.name))
      self.fields["sr%s" % reg.id].initial=True

class QuestionForm(DynamicForm):
  def save(self, gameid):
    game = Game.objects.get(id=gameid)
    game.questionforgame_set.all().delete()

    keys = self.data.keys()
    act_keys = []
    for key in keys:
      if key.find("required") == -1:
        act_keys.append(key)
    for queid in act_keys:
      if self.data[queid]:
        quegame = QuestionForGame.objects.create(question=Question.objects.get(id=queid),
                                                 required=False,
                                                 game=game)
        if self.data["%s_required" % queid]:
          quegame.required = True
        quegame.save()