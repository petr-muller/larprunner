# This Python file uses the following encoding: utf-8
from django import forms
from larprunner.questions.models import QTYPES, Question, ChoicesForQuestion

class CreateQuestionForm(forms.Form):
  
  id        = forms.IntegerField(widget=forms.HiddenInput, required=False)
  uniq_name = forms.CharField(max_length=30,
                              widget=forms.TextInput(),
                              label=u'Unikátní název')
  type      = forms.ChoiceField(choices=QTYPES,
                                label=u'Typ otázky')
  maxlen    = forms.IntegerField( label=u'Maximální délka',
                                  required=False)
  regexp    = forms.CharField(max_length=100,
                              label=u'Regulární výraz',
                              required=False)
  comment   = forms.CharField(label=u'Delší komentář k otázce',
                              widget=forms.Textarea(),
                              required=False)
  choices   = forms.CharField(label=u'Seznam voleb, oddělených znakem "&"',
                              widget=forms.Textarea(),
                              required=False)
  def loadValues(self, queid):
    question = Question.objects.get(id=queid)
    choices = ChoicesForQuestion.objects.filter(question=question)
    self.initial["id"] = question.id
    self.initial["uniq_name"] = question.uniq_name
    self.initial["type"]      = question.type
    self.initial["maxlen"]    = question.maxlen
    self.initial["regexp"]    = question.regexp
    self.initial["comment"]   = question.comment

    self.initial["choices"]   = "&".join([ x.choice for x in choices])

  def save(self):
    modificator = Question.objects.modQuestion
    if self.cleaned_data['id'] == "":
      id = None
    else:
      id = self.cleaned_data['id']

    mod_question = modificator( id = id,
                                uname=self.cleaned_data['uniq_name'],
                                type =self.cleaned_data['type'],
                                maxlen=self.cleaned_data['maxlen'],
                                regexp = self.cleaned_data['regexp'],
                                comment = self.cleaned_data['comment'],
                                choices = self.cleaned_data['choices'].split('&'))
    return mod_question
