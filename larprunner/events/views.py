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
from django.db import transaction
from django.template import RequestContext
from django.newforms.util import smart_unicode

@my_login_required
def triage_messages(request):
  messages = request.user.get_and_delete_messages()
  errors = []
  notif = []

  for message in messages:
    if message[:2] == u"1|":
      errors.append(message[2:])
    elif message[:2] == u"0|":
      notif.append(message[2:])

  if len(notif) == 0:
    notif=None
  if len(errors) == 0:
    errors=None

  return (notif, errors)

@my_login_required
def add_error_message(request, message):
  request.user.message_set.create(message=u"1|"+smart_unicode(message))
  request.user.save()

@my_login_required
def add_notif_message(request, message):
  request.user.message_set.create(message=u"0|"+smart_unicode(message))
  request.user.save()

@my_login_required
def mainpage(request):
  if request.user.is_authenticated():
    user = request.user
    games = Event.objects.filter(Q(state="OPEN") | Q(state="CLOSED"))
    player = Player.objects.get(user=request.user)

    order = "odd"
    for game in games:
      game.check_free_place(player.gender)
      game.check_regged(player)
      game.setTempUrl()
      game.evenity = order
      if order == "odd":
        order = "even"
      else:
        order = "odd"
  notif_messages, error_messages = triage_messages(request)
  return render_to_response("events/mainpage.html",
                            {'user' : user,
                             'games': games,
                             'notif_messages' : notif_messages,
                             'error_messages' : error_messages,
                             })
@my_login_required
def event_unapp(request, eventid):
  event = Event.objects.get(id=eventid)
  player = Player.objects.get(user=request.user)
  event.unregister(player)
  add_notif_message(request, u"%s: odhlášeno" % smart_unicode(event.name) )
  
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
      add_notif_message(request, u"%s: přihláška přijata" % smart_unicode(event.name) )
      return HttpResponseRedirect("/")

  return render_to_response("events/game_app.html",
                            {'user' : request.user,
                             'form' : form,
                             'eventid'  : eventid,
                             })

@transaction.commit_manually
def slots(request, eventid):
  event = Event.objects.get(id=eventid)
  form = SlotAppForm()
  form.loadFromEvent(event,Player.objects.get(user=request.user))
  if request.method == "POST":
    form.setData(request.POST)
    form.validate()
    if form.is_valid():
      if form.save(event, request.user):
        transaction.commit()
        return HttpResponseRedirect(u"/game/%s/slots_change/" % eventid)
      else:
        transaction.rollback()
        form = SlotAppForm()
        form.loadFromEvent(event,Player.objects.get(user=request.user))
        add_error_message(request, message=u"Omlouváme se, došlo k souběhu a během vyplňování formuláře se některé hry zaplnily. Formulář teď zobrazuje aktuální stav.")
  transaction.commit()

  notif_messages, error_messages = triage_messages(request)
  transaction.commit()
  return render_to_response(u"events/slots_app.html",
                            {u'user' : request.user,
                             u'eventid' : eventid,
                             u'form' : form,
                             u'notif_messages' : notif_messages,
                             u'error_messages' : error_messages}
                             )

def slots_change(request, eventid):
  event = Event.objects.get(id=eventid)
  player = Player.objects.get(user=request.user)
  event.mailToPlayer(player)
  games_applied = event.getGamesForPlayer(player)
  if len(games_applied) == 0:
    add_notif_message(request, u"%s: nejste přihlášen na žádnou hru" % smart_unicode(event.name) )
    return HttpResponseRedirect(u"/")

  fields = {}
  for game in games_applied:
    for question in game.game.questionforgame_set.all():
      fields["%s_%s" % (game.id, question.question.id)] = question.asField()
      fields["%s_%s" % (game.id, question.question.id)].label = u"Otázka ke hře %s: %s" % (game.game.name,
                                                                          fields["%s_%s" % (game.id, question.question.id)].label)
  if len(fields) == 0:
    add_notif_message(request, u"%s: registrace na jednotlivé hry byla přijata" % smart_unicode(event.name) )
    return HttpResponseRedirect(u"/")

  form = QuestionsForGamesForm()
  form.setFields(fields)
  if request.method == "POST":
    form.setData(request.POST)
    form.validate("gheee")
    if form.is_valid():
      add_notif_message(request, u"%s: registrace na jednotlivé hry byla přijata" % smart_unicode(event.name) )
      form.save(request.user)
      return HttpResponseRedirect(u"/")
  return render_to_response("events/que_for_games.html",
                            {u"user"    : request.user,
                             u"form"    : form,
                             u"eventid" : eventid})
