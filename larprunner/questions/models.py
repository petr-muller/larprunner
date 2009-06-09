# This Python file uses the following encoding: utf-8

from django import forms
from django.db import models

class QuestionManager(models.Manager):
  def modQuestion(self, id, uname, type, maxlen=0, regexp=None, comment=None,
                  choices = ()):

    if maxlen is None:
      maxlen=0
    if id is None:
      question = Question.objects.create(uniq_name = uname,
                                                type      = type,
                                                maxlen    = maxlen,
                                                regexp    = regexp,
                                                comment   = comment)
    else:
      question = Question.objects.get(id=id)
      question.uniq_name = uname
      question.type = type
      question.maxlen = maxlen
      question.regexp = regexp
      question.comment = comment

    question.save()

    ChoicesForQuestion.objects.filter(question=question).delete()
    if choices.__class__ in [ [].__class__, ().__class__ ] and len(choices) > 1:
      for choice in choices:
        new_choice = ChoicesForQuestion(choice=choice, question = question)
        new_choice.save()

    return question


QTYPES = (
           ('TEXTFIELD',  'Krátký text'),
           ('TEXTAREA',   'Dlouhý text'),
           ('CHECKBOX',   'Checkbox'),
           ('RADIO',      'Radio button'),
           )

class Question(models.Model):
  uniq_name = models.CharField("Unikátní název", max_length=30)
  type      = models.CharField("Typ", choices=QTYPES, max_length=15)
  maxlen    = models.PositiveIntegerField("Maximální délka")
  regexp    = models.CharField("Regulární výraz", max_length=100)
  comment   = models.TextField("Komentář")

  objects = QuestionManager()

  def asField(self, required=True):

    choices = ChoicesForQuestion.objects.filter(question=self)
    choices_prepared=[]
    for choice in choices:
      choices_prepared.append((choice.id, choice.choice))

    if self.type == "TEXTFIELD":
      field = forms.CharField(max_length=self.maxlen,label=self.comment, required=required)
    elif self.type == "TEXTAREA":
      field = forms.CharField(widget=forms.Textarea, label=self.comment, required=required)
    elif self.type == "CHECKBOX":
      field = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=choices_prepared,label=self.comment,required=required)
    elif self.type == "RADIO":
      field = forms.ChoiceField(choices=choices_prepared,label=self.comment,required=required)
    return field

class ChoicesForQuestion(models.Model):
  choice    = models.CharField(max_length=50)
  question  = models.ForeignKey(Question)

class Answer(models.Model):
  question = models.ForeignKey(Question)
  answer = models.TextField()
