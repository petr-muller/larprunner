# This Python file uses the following encoding: utf-8
# Create your views here.
from django.shortcuts import render_to_response
from larprunner.admin.manipulation import my_login_required
from larprunner.events.models import Event, Registration
from larprunner.admin.manipulation import my_login_required
from larprunner.events.forms import ApplicationForm
from larprunner.users.models import Player
from django.http import HttpResponseRedirect

@my_login_required
def mainpage(request):
  if request.user.is_authenticated():
    user = request.user
    games = Event.objects.exclude(state="CREATED")
    player = Player.objects.get(user=request.user)
    regs = Registration.objects.filter(player=player)

  else:
    user = None
  return render_to_response("events/mainpage.html",
                            {'user' : user,
                             'games': games,
                             'regs' : [ reg.event.id for reg in regs ]} )
@my_login_required
def event_unapp(request, eventid):

  Registration.objects.get(player=Player.objects.get(user=request.user), event=Event.objects.get(id=eventid)).delete()

  #print Registration.objects.get(event=Event.objects.filter(id=eventid),
  #                         player=Player.objects.get(user=request.user))


  return HttpResponseRedirect("/")

@my_login_required
def event_app(request, eventid):
  event = Event.objects.get(id=eventid)
  questions = event.question.all()
  fields= {}
  for question in questions:
    fields["%s" % question.id] = question.asField()
  form = ApplicationForm()
  form.setFields(fields)
  if request.method == "POST":
    form.setData(request.POST)
    form.validate(request.POST)
    form.save(eventid, request.user)
    return HttpResponseRedirect("/")
  else:

    player = Player.objects.get(user=request.user)
    already_reg = Registration.objects.filter(player=player).filter(event=event)
    already_registered=False
    if len(already_reg) == 1:
      form.fields["id"].initial = already_reg[0].id
      already_registered=True

  return render_to_response("events/game_app.html",
                            {'user' : request.user,
                             'form' : form,
                             'eventid'  : eventid,
                             'alreg'    : already_registered})