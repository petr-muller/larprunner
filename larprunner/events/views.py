# This Python file uses the following encoding: utf-8
# Create your views here.
from django.shortcuts import render_to_response
from larprunner.admin.manipulation import my_login_required
from larprunner.events.models import Event, Registration, MultiGameSlot
from larprunner.admin.manipulation import my_login_required
from larprunner.events.forms import ApplicationForm, SlotAppForm, QuestionsForGamesForm
from larprunner.users.models import Player
from django.http import HttpResponseRedirect
from django.db.models import Q

@my_login_required
def mainpage(request):
  if request.user.is_authenticated():
    user = request.user
    games = Event.objects.filter(Q(state="OPEN") | Q(state="CLOSED"))
    player = Player.objects.get(user=request.user)

    for game in games:
      game.check_free_place(player.gender)
      game.check_regged(player)
      game.setTempUrl()

  return render_to_response("events/mainpage.html",
                            {'user' : user,
                             'games': games,
                             })
@my_login_required
def event_unapp(request, eventid):
  event = Event.objects.get(id=eventid)
  player = Player.objects.get(user=request.user)
  event.unregister(player)

  return HttpResponseRedirect("/")

@my_login_required
def event_app(request, eventid):
  event = Event.objects.get(id=eventid)
  questions_for_event = event.question.all()
  questions_for_game = []
  if event.game is not None:
    questions_for_game = event.game.questionforgame_set.all()
  fields= {}
  for question in questions_for_event:
    fields["%s" % question.question.id] = question.asField()
  for question in questions_for_game:
    fields["%s" % question.question.id] = question.asField()
    fields["%s" % question.question.id].label = u"Otázka ke hře %s: %s" % (event.game.name,
                                                                          fields["%s" % question.question.id].label)

  form = ApplicationForm()
  form.setFields(fields)
  if request.method == "POST":
    form.setData(request.POST)
    form.validate(request.POST)
    if form.is_valid():
      form.save(eventid, request.user)
      return HttpResponseRedirect("/")

  return render_to_response("events/game_app.html",
                            {'user' : request.user,
                             'form' : form,
                             'eventid'  : eventid,
                             })

def slots(request, eventid):
  event = Event.objects.get(id=eventid)
  form = SlotAppForm()
  form.loadFromEvent(event,Player.objects.get(user=request.user))
  if request.method == "POST":
    form.setData(request.POST)
    form.validate()
    if form.is_valid():
      form.save(event, request.user)
      return HttpResponseRedirect(u"/game/%s/slots_change/" % eventid)
  return render_to_response(u"events/slots_app.html",
                            {u'user' : request.user,
                             u'eventid' : eventid,
                             u'form' : form })

def slots_change(request, eventid):
  event = Event.objects.get(id=eventid)
  player = Player.objects.get(user=request.user)

  games_applied = event.getGamesForPlayer(player)
  if len(games_applied) == 0:
    return HttpResponseRedirect(u"/")
  print games_applied
  fields = {}
  for game in games_applied:
    for question in game.game.questionforgame_set.all():
      fields["%s_%s" % (game.id, question.question.id)] = question.asField()
      fields["%s_%s" % (game.id, question.question.id)].label = u"Otázka ke hře %s: %s" % (game.game.name,
                                                                          fields["%s_%s" % (game.id, question.question.id)].label)

  form = QuestionsForGamesForm()
  form.setFields(fields)
  if request.method == "POST":
    form.setData(request.POST)
    form.validate("gheee")
    if form.is_valid():
      form.save(request.user)
      return HttpResponseRedirect(u"/")
  print form
  return render_to_response("events/que_for_games.html",
                            {u"user"    : request.user,
                             u"form"    : form,
                             u"eventid" : eventid})
