# This Python file uses the following encoding: utf-8
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.newforms import form_for_instance, form_for_model, BooleanField
from django.newforms.widgets import Textarea, TextInput, Select, HiddenInput, CheckboxInput
from django.shortcuts import render_to_response
from django.template import RequestContext
from forms import SlotForm
from larprunner.events.forms import RegistrationForm, SingleEventForm, MultiEventForm
from larprunner.events.models import Event, MultiGameSlot, GameInSlot, Registration
from manipulation import my_login_required, createMenuItems, my_admin_required
from models import Game, Log
from larprunner.questions.models import Question


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
      data = {}
      our_questions = event.question.filter(event=event)

      for question in questions:
        fields["%s" % question.id] = BooleanField(label=question.uniq_name, required=False, widget=CheckboxInput)        
        if question in our_questions:          
          fields["%s" % question.id].initial = True
      
      reg.setFields(fields)
      reg.setData(data)

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
    print form
    
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
def show_applied_people(request, eventid):
  event = Event.objects.get(id=eventid)
  regs = Registration.objects.filter(event=event).order_by("player")
  people = [ reg.player for reg in regs ]
  people.sort(lambda x,y: cmp(x.surname, y.surname))
  
  return render_to_response('admin/eventpeople.html',
                              {'menuitems'    : createMenuItems(),
                               'title'        : "Lidé přihlášení na %s" % event.name,
                               'user'         : request.user,
                               'people'       : people},
                              )