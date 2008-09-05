# This Python file uses the following encoding: utf-8

from django.db import models

class QuestionManager(models.Manager):
  def addQuestion(self, uname, type, maxlen=None, regexp=None, comment=None,
                  choices = ()):
    question = Question.objects.create_object(uniq_name = uname,
                                              type      = type,
                                              maxlen    = int(maxlen),
                                              regexp    = regexp,
                                              comment   = comment)
    question.save()
    for choice in choices:
      new_choice = ChoicesForQuestion(choice=choice, question = question)
    
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
  
class ChoicesForQuestion(models.Model):
  choice    = models.CharField(maxlength=50)
  question  = models.ForeignKey(Question)