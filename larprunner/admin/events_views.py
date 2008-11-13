# This Python file uses the following encoding: utf-8
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.newforms import form_for_instance, form_for_model, BooleanField
from django.newforms.widgets import Textarea, TextInput, Select, HiddenInput, CheckboxInput
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

@my_admin_required
def overview(request):
  logs = Log.objects.order_by("-id")[:10]
  return render_to_response("admin/overview.html",
                            { 'logs'      : logs,
                              'menuitems' : createMenuItems("overview"),
                              'user'      : request.user,
                              'title'     : u'Přehled'})

@my_admin_required
def events(request):
  return render_to_response("admin/events.html",
                            { 'menuitems' : createMenuItems('events'),
                              'events_s'  : Event.objects.filter(type="single"),
                              'events_m'  : Event.objects.filter(type="multi"),
                              'user'      : request.user,
                              'title'     : "Eventy"  }
                            )

@my_admin_required
def modify(request, eventid=None, type="single", regcreate=None):

  if type == "single":
    Form  = SingleEventForm
  else:
    Form  = MultiEventForm

  if request.method == 'POST':
    if regcreate is not None:
      form = RegistrationForm()
      fields={}
      for question in Question.objects.all():
        fields["%s" % question.id] = BooleanField(label=question.uniq_name, widget=CheckboxInput)
        fields["%s_required" % question.id] = BooleanField(label="  %s povinne" % question.uniq_name, required=False, widget=CheckboxInput)
      form.setFields(fields)
      form.setData(request.POST)
      form.validate(request.POST)
    else:
      form = Form(request.POST)

    form.save(eventid)
    return HttpResponseRedirect('/admin/events/%s/%s/' % (type, eventid))
  else:

    form = Form()
    event = None
    slots = None
    reg   = None
    if eventid != "new":
      event = Event.objects.get(id=eventid)
      form.loadValues(event)
      slots = MultiGameSlot.objects.filter(event=event)
      questions = Question.objects.all()
      reg = RegistrationForm()
      fields = {}
      our_questions = event.question

      for question in questions:
        fields["%s" % question.id] = BooleanField(label=question.uniq_name, required=False, widget=CheckboxInput)
        fields["%s_required" % question.id] = BooleanField(label="  %s povinne" % question.uniq_name, required=False, widget=CheckboxInput)

        if question in [ que.question for que in our_questions.all() ]:
          fields["%s" % question.id].initial = True
          if our_questions.get(question=question).required:
            fields["%s_required" % question.id].initial = True


      reg.setFields(fields)

  return render_to_response('admin/eventform.html',
                            {'form'         : form,
                             'eventid'      : eventid,
                             'menuitems'    : createMenuItems(),
                             'user'         : request.user,
                             'title'        : "Vlastnosti hry",
                             'event'        : event,
                             'slots'        : slots,
                             'reg'          : reg
                             }
                            )
  
@my_admin_required
def slot_modify(request, eventid, slotid=None):
  if slotid == "new":
    ActualSlotForm = form_for_model(MultiGameSlot)
    log_message = u"Pro event %s přidán slot"
    sgf = None
    slotid = None

  else:
    inst = MultiGameSlot.objects.get(id=slotid)
    ActualSlotForm = form_for_instance(inst)
    log_message = u"V eventu %s změněn slot"
    sgf = SlotForm(slotid)
  if request.method == 'POST':
    form = ActualSlotForm(request.POST)
    if form.is_valid():
      form.save()
      log = Log(user=request.user,
                message=log_message+" "+form.clean_data['name'])
      log.save()
      request.user.message_set.create(message=u"V eventu %s změněn slot")
      return HttpResponseRedirect('/admin/events/multi/%s/' % eventid )
  else:
    form = ActualSlotForm()
    form.initial['event'] = eventid
    form.fields['event'].choices = ((eventid,"LARP"),)


  return render_to_response('admin/slotform.html',
                              {'form'         : form,
                               'slotform'     : sgf,
                               'slotid'       : slotid,
                               'menuitems'    : createMenuItems(),
                               'eventid'      : eventid,
                               'gamespresent' : GameInSlot.objects.filter(slot=slotid),
                               'title'        : "Editace slotu",
                               'user'         : request.user},
                              )
@my_admin_required
def add_game_to_slot(request, eventid="", slotid=""):
  if request.method == "POST":
    form = SlotForm(slotid, request.POST)

    if form.is_valid():
      tmp = GameInSlot(game=Game.objects.get(id=int(form.clean_data['games'])),
                       slot=MultiGameSlot.objects.get(id=int(form.clean_data['slot'])),
                       price=form.clean_data['price'],
                       note=form.clean_data['note'])
      tmp.save()
      return HttpResponseRedirect('/admin/events/multi/%s/slots/%s/' % (eventid, slotid))
    else:
      return HttpResponseRedirect('/admin/events/multi/%s/slots/%s/' % (eventid, slotid))
  else:
    return HttpResponseRedirect('/admin/events/multi/%s/slots/%s/' % (eventid, slotid))

@my_admin_required
def show_applied_people(request, eventid, slotted=False):
  event = Event.objects.get(id=eventid)
  regs = Registration.objects.filter(event=event).order_by("player")
  people = [ reg.player for reg in regs ]
  people.sort(lambda x,y: cmp(x.surname, y.surname))

  headlines = [ "Jméno", "Telefon", "Email", "Rok narození"] + [ que.question.uniq_name for que in event.question.all() ]
  if event.game is not None:
    headlines.extend([ que.question.uniq_name for que in event.game.questionforgame_set.all() ])
  if slotted and event.type == "multi":
    slots = MultiGameSlot.objects.filter(event=event)
    headlines.extend([ slot.name for slot in slots ])
  else:
    slots=[]
  cells = []
  for player in people:
    row   = [ "%s, %s (%s)" %  (player.surname, player.name, player.nick) ]
    row  += [ player.phone, player.user.email, player.year_of_birth]
    reg   = Registration.objects.get(player=player, event=event)
    for question in [ que.question for que in event.question.all()]:
      answers = reg.answers.filter(question=question)
      row += [ ",".join( [ ans.answer for ans in answers ]) ]
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
  return render_to_response('admin/people_in_slots.html',
                            {'menuitems'      : createMenuItems(),
                             'title'          : 'Sloty v %s' % event.name,
                             'user'           : request.user,
                             'slots'          : slots,
                             'eventid'        : eventid})

@my_admin_required
def delete_slot(request, eventid, slotid):
  slot = MultiGameSlot.objects.get(id=slotid)
  slot.delete()
  return HttpResponseRedirect('/admin/events/multi/%s/' % (eventid,))

@my_admin_required
def delete_game_from_slot(request, eventid, slotid, gameid):
  game = GameInSlot.objects.get(id=gameid)
  game.delete()
  return HttpResponseRedirect('/admin/events/multi/%s/slots/%s/' % (eventid, slotid))

@my_admin_required
def slot_details(request, eventid, slotid):
  game = GameInSlot.objects.get(id=slotid)
  regs = SlotGameRegistration.objects.filter(slot=game).order_by("player")
  headlines = [ "Jméno"] + [ que.question.uniq_name for que in game.game.questionforgame_set.all() ]
  people = [ reg.player for reg in regs ]
  people.sort(lambda x,y: cmp(x.surname, y.surname))
  rows = []
  for person in people:
    cols = [ person.name + person.surname + "(" + person.nick + ")" ]
    registration = SlotGameRegistration.objects.get(slot=game, player=person)
    for question in game.game.questionforgame_set.all():
      answers = registration.answers.filter(question=question.question)
      cols += [ ",".join( [ ans.answer for ans in answers ]) ]
    rows.append(cols)

  return render_to_response("admin/slot_details.html",
                            {"menuitems"      : createMenuItems(),
                             'title'          : "Detaily slotu",
                             'user'           : request.user,
                             'game'           : game,
                             'rows'           : rows,
                             'headlines'      : headlines})

@my_admin_required
def slotregistration_action(request, eventid=None):
  ids = []
  for key in request.POST.keys():
    if key[:2] == "sr":
      try:
        ids.append(int(key[2:]))
      except ValueError:
        pass

  filterer = Q(id=None)
  for id in ids:
    filterer = filterer | Q(id=id)

  affected_sgrs = SlotGameRegistration.objects.filter(filterer)
  if len(affected_sgrs) == 0:
    return HttpResponseRedirect('/admin/events/multi/%s/people_at_slots/' % eventid)

  if 'unregister_with_mail' in request.POST.keys():
    form = ThrowOutForm()
    form.load(affected_sgrs)
    return render_to_response("admin/throwout.html",
                              {'form': form,
                               "menuitems"      : createMenuItems(),
                               'title'          : "Odhlášení účastníků",
                               'eventid'        : eventid,
                              })
  elif 'unregister_and_send_mails' in request.POST.keys():
    lists = {}
    for reg in affected_sgrs:
      email = reg.player.user.email
      if not lists.has_key(email):
        lists[email] = []
      lists[email].append("Akce %s, slot %s, hra %s" % (reg.slot.slot.event.name,
                                                       reg.slot.slot.name,
                                                       reg.slot.game.name))

    for mail in lists.keys():
      message = render_to_string('admin/throwout.txt',
                                 {'message' : request.POST['mail'],
                                  'games' : lists[mail]})
      from django.core.mail import send_mail
      subject = "%s - odhlášení z her" % settings.SITE_NAME
      subject = ''.join(subject.splitlines())
      send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

    affected_sgrs.delete()
  elif 'unregister' in request.POST.keys():
    affected_sgrs.delete()
  return HttpResponseRedirect('/admin/events/multi/%s/people_at_slots/' % eventid)