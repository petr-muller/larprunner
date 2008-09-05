# This Python file uses the following encoding: utf-8
from django import newforms as forms
from questions.models import QTYPES


class CreateQuestionForm(forms.Form):
  uniq_name = forms.CharField(max_length=30,
                              widget=forms.TextInput(),
                              label=u'Unikátní název')
  type      = forms.ChoiceField(choices=QTYPES,
                                label=u'Typ otázky')
  maxlen    = forms.PositiveIntegerField(label=u'Maximální délka')
  regexp    = forms.CharField(max_length=100,
                              label=u'Regulární výraz')
  comment   = forms.Textarea(label=u'Komentář, zobrazený u pole')
  choices   = forms.Textarea(label=u'Volby, oddělené znakem "&"')

