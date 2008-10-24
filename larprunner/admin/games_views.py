# This Python file uses the following encoding: utf-8
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from manipulation import my_login_required, createMenuItems, my_admin_required
from models import Game, Log, QuestionForGame
from django.newforms import form_for_instance, form_for_model
from django.newforms import ChoiceField, BooleanField
from django.template import RequestContext
from forms import SlotForm, QuestionForm
from larprunner.questions.models import Question
from django.newforms.widgets import CheckboxInput

@my_admin_required
def administrate_games(request):
  games = Game.objects.all()
  return render_to_response("admin/games.html", 
                            {'games'     : games,
                             'menuitems' : createMenuItems("games"),
                             'user'      : request.user,
                             'title'     : "Hry",
                             })

@my_admin_required
def game_modify(request, gameid=None, qmod=False):
  question_form = None 
  if gameid == "new":
    GameForm = form_for_model(Game)
  else:
    inst = Game.objects.get(id=gameid)
    GameForm = form_for_instance(inst)

    questions = Question.objects.all()
    question_form = QuestionForm()
    fields = {}
    our_questions = inst.questionforgame_set

    for question in questions:
      fields["%s" % question.id] = BooleanField(label=question.uniq_name, required=False, widget=CheckboxInput)
      fields["%s_required" % question.id] = BooleanField(label="  %s povinne" % question.uniq_name, required=False, widget=CheckboxInput)

      if question in [ que.question for que in our_questions.all() ]:
        fields["%s" % question.id].initial = True
        if our_questions.get(question=question).required:
          fields["%s_required" % question.id].initial = True
    question_form.setFields(fields)

  if request.method == 'POST':
    if qmod:
      form = QuestionForm()
      fields={}
      for question in Question.objects.all():
        fields["%s" % question.id] = BooleanField(label=question.uniq_name, required=False, widget=CheckboxInput)
        fields["%s_required" % question.id] = BooleanField(label="  %s povinne" % question.uniq_name, required=False, widget=CheckboxInput)
      form.setFields(fields)
      form.setData(request.POST)
      form.validate(request.POST)
      if form.is_valid():
        form.save(gameid)
        return HttpResponseRedirect('/admin/games/')
    else:
      form = GameForm(request.POST)
      if form.is_valid():
        form.save()
        return HttpResponseRedirect('/admin/games/')
  else:
    form = GameForm()
  return render_to_response('admin/gameform.html', 
                            {'form': form, 'gameid': gameid,
                             'menuitems'  : createMenuItems(),
                             'user'       : request.user,
                             'title'      : "Editace hry",
                             'questions'  : question_form})

@my_admin_required
def game_delete(request, gameid=None):
  if gameid is not None:    
    game = Game.objects.get(id=gameid)
    log = Log(user=request.user, message="Smazána hra"+" "+ game.name)
    log.save()
    game.delete()
    request.user.message_set.create(message=u"Hra úspěšně smazána")    
  return HttpResponseRedirect('/admin/games/')    
