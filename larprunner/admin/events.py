# This Python file uses the following encoding: utf-8
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from manipulation import my_login_required, createMenuItems, my_admin_required
from models import Game, Log, EventOneGame, EventMultiGame, MultiGameSlot, GameInSlot
from django.newforms import form_for_instance, form_for_model
from django.newforms.widgets import Textarea
from django.template import RequestContext
from forms import SlotForm

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
                              'events_s'  : EventOneGame.objects.all(),
                              'events_m'  : EventMultiGame.objects.all(),
                              'user'      : request.user,
                              'title'     : "Eventy"  }
                            )

@my_admin_required
def modify(request, eventid=None, type="single"):
  chosen_model = {'single' : EventOneGame, 'multi' : EventMultiGame}
  create_log   = {'single' : u"Vytvořen event s jednou hrou",
                  'multi'  : u"Vytvořen event s více hrami"}
  change_log   = {'single' : u"Změněn event s jednou hrou",
                  'multi'  : u"Změněn event s více hrami"}
  forms        = {'single' : "admin/singleeventform.html",
                  'multi'  : "admin/multieventform.html"}
  slots = ()
  allow_slots = False
  if eventid == "new":
    EventForm = form_for_model(chosen_model[type])
    log_message = create_log[type]
  else:
    inst = chosen_model[type].objects.get(id=eventid)
    EventForm = form_for_instance(inst)
    log_message = change_log[type]    
    if type == 'multi':             
      slots = MultiGameSlot.objects.filter(event=eventid)      
      allow_slots = 1
  if request.method == 'POST':
    form = EventForm(request.POST)
    if form.is_valid():
      form.save()
      log = Log(user=request.user, 
                message=log_message+" "+form.clean_data['name'])
      log.save()
      request.user.message_set.create(message=change_log[type])
      return HttpResponseRedirect('/admin/events/')
  else:
    EventForm.base_fields['fluff'].widget = Textarea(attrs={'rows': 5,
                                                            'cols': 20})
    form = EventForm()
  return render_to_response(forms[type], 
                            {'form'         : form,
                             'eventid'      : eventid,
                             'menuitems'    : createMenuItems(),
                             'allow_slots'  : allow_slots,
                             'slots'        : slots,
                             'user'         : request.user,
                             'title'        : "Vlastnosti jednorázové hry" },
                             
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
  return render_to_response('admin/slotform.html',
                              {'form'         : form,
                               'slotform'     : sgf,
                               'slotid'       : slotid,
                               'menuitems'    : createMenuItems(),
                               'eventid'      : eventid,
                               'gamespresent' : GameInSlot.objects.filter(slot=slotid),
                               'title'        : "Editace slotu",
                               'uset'         : request.user},
                              )

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
  

     
    