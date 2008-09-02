# This Python file uses the following encoding: utf-8
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from manipulation import my_login_required, createMenuItems, my_admin_required
from models import Game, Log, EventOneGame, EventMultiGame, MultiGameSlot, GameInSlot
from django.newforms import form_for_instance, form_for_model
from django.newforms import ChoiceField
from django.template import RequestContext
from forms import SlotForm

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
def game_modify(request, gameid=None):
  if gameid == "new":
    GameForm = form_for_model(Game)
    log_message = u"Vytvořena hra"
  else:
    inst = Game.objects.get(id=gameid)
    GameForm = form_for_instance(inst)
    log_message = u"Změněna hra"
  if request.method == 'POST':
    form = GameForm(request.POST)
    if form.is_valid():
      form.save()
      log = Log(user=request.user, message=log_message+" "+form.clean_data['name'])
      log.save() 
      request.user.message_set.create(message=u"Hra úspěšně uložena")      
      return HttpResponseRedirect('/admin/games/')
  else:
    form = GameForm()
  return render_to_response('admin/gameform.html', 
                            {'form': form, 'gameid': gameid,
                             'menuitems'  : createMenuItems(),
                             'user'       : request.user,
                             'title'      : "Editace hry"})

@my_admin_required
def game_delete(request, gameid=None):
  if gameid is not None:    
    game = Game.objects.get(id=gameid)
    log = Log(user=request.user, message="Smazána hra"+" "+ game.name)
    log.save()
    game.delete()
    request.user.message_set.create(message=u"Hra úspěšně smazána")    
  return HttpResponseRedirect('/admin/games/')    