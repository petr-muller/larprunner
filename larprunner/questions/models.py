# This Python file uses the following encoding: utf-8

from django import newforms as forms
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
  uniq_name = models.CharField("Unikátní název", maxlength=30)
  type      = models.CharField("Typ", choices=QTYPES, maxlength=15)
  maxlen    = models.PositiveIntegerField("Maximální délka")
  regexp    = models.CharField("Regulární výraz", maxlength=100)
  comment   = models.TextField("Komentář")

  objects = QuestionManager()

  def asField(self):

    choices = ChoicesForQuestion.objects.filter(question=self)
    choices_prepared=[]
    for choice in choices:
      choices_prepared.append((choice.id, choice.choice))

    if self.type == "TEXTFIELD":
      field = forms.CharField(maxlen=self.maxlen,label=self.comment)
    elif self.type == "TEXTAREA":
      field = forms.CharField(widget=forms.Textarea, label=self.comment, )
    elif self.type == "CHECKBOX":
      field = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=choices_prepared,label=self.comment)
    elif self.type == "RADIO":
      field = forms.ChoiceField(choices=choices_prepared,label=self.comment)
    return field

class ChoicesForQuestion(models.Model):
  choice    = models.CharField(maxlength=50)
  question  = models.ForeignKey(Question)

class Answer(models.Model):
  question = models.ForeignKey(Question)
  answer = models.TextField()