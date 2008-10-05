# This Python file uses the following encoding: utf-8
# Create your views here.
from django.shortcuts import render_to_response
from larprunner.admin.manipulation import my_login_required
from larprunner.events.models import Event, Registration, MultiGameSlot
from larprunner.admin.manipulation import my_login_required
from larprunner.events.forms import ApplicationForm, SlotAppForm
from larprunner.users.models import Player
from django.http import HttpResponseRedirect

@my_login_required
def mainpage(request):
  if request.user.is_authenticated():
    user = request.user
    games = Event.objects.exclude(state="CREATED")
    player = Player.objects.get(user=request.user)

    for game in games:
      game.check_free_place(player.gender)
      game.check_regged(player)
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
  questions = event.question.all()
  fields= {}
  for question in questions:
    fields["%s" % question.question.id] = question.asField()
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
      return HttpResponseRedirect("/")

  return render_to_response("events/slots_app.html",
                            {'user' : request.user,
                             'eventid' : eventid,
                             'form' : form })