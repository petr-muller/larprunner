# This Python file uses the following encoding: utf-8
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.forms import form_for_instance, form_for_model, BooleanField
from django.forms.widgets import Textarea, TextInput, Select, HiddenInput, CheckboxInput
from django.shortcuts import render_to_response
from django.template import RequestContext
from forms import SlotForm, ThrowOutForm
from larprunner.events.forms import RegistrationForm, SingleEventForm, MultiEventForm
from larprunner.events.models import Event, MultiGameSlot, GameInSlot, Registration, SlotGameRegistration
from larprunner.questions.models import Question
from manipulation import my_login_required, createMenuItems, my_admin_required
from models import Game, Log
from django.template.loader import render_to_string
from django.conf import settings
from django.http import HttpResponse
from django.core.mail import send_mail

@my_admin_required
def overview(request):
  logs = Log.objects.order_by(u"-id")[:10]
  return render_to_response(u"admin/overview.html",
                            { u'logs'      : logs,
                              u'menuitems' : createMenuItems(u"overview"),
                              u'user'      : request.user,
                              u'title'     : u'Přehled'})

@my_admin_required
def events(request):
  return render_to_response(u"admin/events.html",
                            { u'menuitems' : createMenuItems(u'events'),
                              u'events_s'  : Event.objects.filter(type=u"single"),
                              u'events_m'  : Event.objects.filter(type=u"multi"),
                              u'user'      : request.user,
                              u'title'     : u"Eventy"  }
                            )

@my_admin_required
def modify(request, eventid=None, type=u"single", regcreate=None):

  if type == u"single":
    Form  = SingleEventForm
  else:
    Form  = MultiEventForm

  if request.method == u'POST':
    if regcreate is not None:
      form = RegistrationForm()
      fields={}
      for question in Question.objects.all():
        fields[u"%s" % question.id] = BooleanField(label=question.uniq_name, widget=CheckboxInput)
        fields[u"%s_required" % question.id] = BooleanField(label=u"  %s povinné" % question.uniq_name, required=False, widget=CheckboxInput)
      form.setFields(fields)
      form.setData(request.POST)
      form.validate(request.POST)
    else:
      form = Form(request.POST)

    form.save(eventid)
    return HttpResponseRedirect(u'/admin/events/%s/%s/' % (type, eventid))
  else:

    form = Form()
    event = None
    slots = None
    reg   = None
    if eventid != u"new":
      event = Event.objects.get(id=eventid)
      form.loadValues(event)
      slots = MultiGameSlot.objects.filter(event=event)
      questions = Question.objects.all()
      reg = RegistrationForm()
      fields = {}
      our_questions = event.question

      for question in questions:
        fields[u"%s" % question.id] = BooleanField(label=question.uniq_name, required=False, widget=CheckboxInput)
        fields[u"%s_required" % question.id] = BooleanField(label=u"  %s povinne" % question.uniq_name, required=False, widget=CheckboxInput)

        if question in [ que.question for que in our_questions.all() ]:
          fields[u"%s" % question.id].initial = True
          if our_questions.get(question=question).required:
            fields[u"%s_required" % question.id].initial = True


      reg.setFields(fields)

  return render_to_response(u'admin/eventform.html',
                            {u'form'         : form,
                             u'eventid'      : eventid,
                             u'menuitems'    : createMenuItems(),
                             u'user'         : request.user,
                             u'title'        : u"Vlastnosti hry",
                             u'event'        : event,
                             u'slots'        : slots,
                             u'reg'          : reg
                             }
                            )
  
@my_admin_required
def slot_modify(request, eventid, slotid=None):
  if slotid == u"new":
    ActualSlotForm = form_for_model(MultiGameSlot)
    log_message = u"Pro event %s přidán slot"
    sgf = None
    slotid = None

  else:
    inst = MultiGameSlot.objects.get(id=slotid)
    ActualSlotForm = form_for_instance(inst)
    log_message = u"V eventu %s změněn slot"
    sgf = SlotForm(slotid)
  if request.method == u'POST':
    form = ActualSlotForm(request.POST)
    if form.is_valid():
      form.save()
      log = Log(user=request.user,
                message=log_message+" "+form.cleaned_data[u'name'])
      log.save()
      request.user.message_set.create(message=u"V eventu %s změněn slot")
      return HttpResponseRedirect(u'/admin/events/multi/%s/' % eventid )
  else:
    form = ActualSlotForm()
    form.initial[u'event'] = eventid
    form.fields[u'event'].choices = ((eventid,u"LARP"),)


  return render_to_response(u'admin/slotform.html',
                              {u'form'         : form,
                               u'slotform'     : sgf,
                               u'slotid'       : slotid,
                               u'menuitems'    : createMenuItems(),
                               u'eventid'      : eventid,
                               u'gamespresent' : GameInSlot.objects.filter(slot=slotid),
                               u'title'        : u"Editace slotu",
                               u'user'         : request.user},
                              )
@my_admin_required
def add_game_to_slot(request, eventid="", slotid=""):
  if request.method == u"POST":
    form = SlotForm(slotid, request.POST)

    if form.is_valid():
      tmp = GameInSlot(game=Game.objects.get(id=int(form.cleaned_data[u'games'])),
                       slot=MultiGameSlot.objects.get(id=int(form.cleaned_data['slot'])),
                       price=form.cleaned_data[u'price'],
                       note=form.cleaned_data[u'note'])
      tmp.save()
      return HttpResponseRedirect(u'/admin/events/multi/%s/slots/%s/' % (eventid, slotid))
    else:
      return HttpResponseRedirect(u'/admin/events/multi/%s/slots/%s/' % (eventid, slotid))
  else:
    return HttpResponseRedirect(u'/admin/events/multi/%s/slots/%s/' % (eventid, slotid))

@my_admin_required
def show_applied_people(request, eventid, slotted=False, cvsexport=False):
  event = Event.objects.get(id=eventid)
  regs = Registration.objects.filter(event=event).order_by(u"player")
  people = [ reg.player for reg in regs ]
  people.sort(lambda x,y: cmp(x.surname, y.surname))

  headlines = [ u"Jméno", u"Telefon", u"Email", u"Rok narození"] + [ que.question.uniq_name for que in event.question.all() ]
  if event.game is not None:
    headlines.extend([ que.question.uniq_name for que in event.game.questionforgame_set.all() ])
  if slotted and event.type == "multi":
    slots = MultiGameSlot.objects.filter(event=event)
    headlines.extend([ slot.name for slot in slots ])
  else:
    slots=[]
  cells = []
  for player in people:
    row   = [ u"%s, %s (%s)" %  (player.surname, player.name, player.nick) ]
    row  += [ player.phone, player.user.email, player.year_of_birth]
    reg   = Registration.objects.get(player=player, event=event)
    for question in [ que.question for que in event.question.all()]:
      answers = reg.answers.filter(question=question)
      row += [ u",".join( [ ans.answer for ans in answers ]) ]
    if event.game is not None:
      for question in [ que.question for que in event.game.questionforgame_set.all()]:
        answers = reg.answers.filter(question=question)
        row += [ ",".join( [ ans.answer for ans in answers ]) ]
    for slot in slots:
      game = slot.getGameForPlayer(player)
      if game:
        row.append(game.game.name)
      else:
        row.append("--nic---")
    cells.append(row)
  
  if cvsexport:
    cells = [headlines] + cells
    print cells
    return HttpResponse("\n".join([",".join([ '"%s"' % str(elm) for elm in row]) for row in cells ]), mimetype="text/plain")

  return render_to_response('admin/eventpeople.html',
                              {'menuitems'    : createMenuItems(),
                               'title'        : "Lidé přihlášení na %s" % event.name,
                               'user'         : request.user,
                               'cells'        : cells,
                               'headers'      : headlines,
                               'event'        : event},
                              )

@my_admin_required
def show_applied_people_in_slots(request, eventid):
  event = Event.objects.get(id=eventid)
  slots = event.multigameslot_set.all()
  for slot in slots:
    slot.printify()
  return render_to_response(u'admin/people_in_slots.html',
                            {u'menuitems'      : createMenuItems(),
                             u'title'          : u'Sloty v %s' % event.name,
                             u'user'           : request.user,
                             u'slots'          : slots,
                             u'eventid'        : eventid})

@my_admin_required
def delete_slot(request, eventid, slotid):
  slot = MultiGameSlot.objects.get(id=slotid)
  slot.delete()
  return HttpResponseRedirect(u'/admin/events/multi/%s/' % (eventid,))

@my_admin_required
def delete_game_from_slot(request, eventid, slotid, gameid):
  game = GameInSlot.objects.get(id=gameid)
  game.delete()
  return HttpResponseRedirect(u'/admin/events/multi/%s/slots/%s/' % (eventid, slotid))

@my_admin_required
def slot_details(request, eventid, slotid):
  game = GameInSlot.objects.get(id=slotid)
  regs = SlotGameRegistration.objects.filter(slot=game).order_by("player")
  headlines = [ "Jméno", "Telefon" ] + [ que.question.uniq_name for que in game.game.questionforgame_set.all() ]
  people = [ reg.player for reg in regs ]
  people.sort(lambda x,y: cmp(x.surname, y.surname))
  rows = []
  for person in people:
    cols = [ person.name + " " + person.surname + " (" + person.nick + ")", person.phone ]
    registration = SlotGameRegistration.objects.get(slot=game, player=person)
    for question in game.game.questionforgame_set.all():
      answers = registration.answers.filter(question=question.question)
      cols += [ u",".join( [ ans.answer for ans in answers ]) ]
    rows.append(cols)

  return render_to_response(u"admin/slot_details.html",
                            {u"menuitems"      : createMenuItems(),
                             u'title'          : u"Detaily slotu",
                             u'user'           : request.user,
                             u'game'           : game,
                             u'rows'           : rows,
                             u'headlines'      : headlines})

@my_admin_required
def slotregistration_action(request, eventid=None):
  ids = []
  for key in request.POST.keys():
    if key[:2] == u"sr":
      try:
        ids.append(int(key[2:]))
      except ValueError:
        pass

  filterer = Q(id=None)
  for id in ids:
    filterer = filterer | Q(id=id)

  affected_sgrs = SlotGameRegistration.objects.filter(filterer)
  if len(affected_sgrs) == 0:
    return HttpResponseRedirect(u'/admin/events/multi/%s/people_at_slots/' % eventid)

  if u'unregister_with_mail' in request.POST.keys():
    form = ThrowOutForm()
    form.load(affected_sgrs)
    return render_to_response(u"admin/throwout.html",
                              {u'form': form,
                               u"menuitems"      : createMenuItems(),
                               u'title'          : u"Odhlášení účastníků",
                               u'eventid'        : eventid,
                              })
  elif u'unregister_and_send_mails' in request.POST.keys():
    lists = {}
    for reg in affected_sgrs:
      email = reg.player.user.email
      if not lists.has_key(email):
        lists[email] = []
      lists[email].append(u"Akce %s, slot %s, hra %s" % (reg.slot.slot.event.name,
                                                       reg.slot.slot.name,
                                                       reg.slot.game.name))

    for mail in lists.keys():
      message = render_to_string(u'admin/throwout.txt',
                                 {u'message' : request.POST[u'mail'],
                                  u'games' : lists[mail]})
      subject = u"%s - odhlášení z her" % settings.SITE_NAME
      subject = ''.join(subject.splitlines())
      send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

    affected_sgrs.delete()
  elif u'unregister' in request.POST.keys():
    affected_sgrs.delete()
  return HttpResponseRedirect(u'/admin/events/multi/%s/people_at_slots/' % eventid)
