# This Python file uses the following encoding: utf-8
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from manipulation import my_login_required, createMenuItems
from models import Game
from django.newforms import form_for_instance, form_for_model

def signup(request):
  username = request.POST.get('username', None)
  password = request.POST.get('password', None)
  if None not in (username, password):
    user = authenticate(username=username, password=password)
    if user is not None and user.is_active:      
      login(request, user)
      next = request.GET.get('next', None)
      if next is None:
        next = "/admin/start/"
      return HttpResponseRedirect(next)
    else:
      #FIXME:generate some sane message
      return HttpResponseRedirect('/admin/login/')    
  else:
    #FIXME: generate some sane messages
    return HttpResponseRedirect('/admin/login/')

def admlogin(request):
  next = request.GET.get('next', None)
  if next is not None:
    next = "?next=%s" % next
  else:
    next = ""

  return render_to_response("admin/loginscreen.html", {'action' : '/admin/signup/%s' % next})

@my_login_required
def hello(request):
  return render_to_response("admin/hello.html", {'username': "Admiral Kokotov"})

@my_login_required
def games(request):
  games = Game.objects.all()
  return render_to_response("admin/games.html", {'games': games, 'menuitems' : createMenuItems("games")})

@my_login_required
def game_modify(request, gameid=None):
  if gameid is None:
    GameForm = form_for_model(Game)
  else:
    inst = Game.objects.get(id=gameid)
    GameForm = form_for_instance(inst)
  if request.method == 'POST':
    form = GameForm(request.POST)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect('/admin/games/')
  else:
    form = GameForm()
  return render_to_response('admin/gameform.html', {'form': form, 'gameid': gameid, 'menuitems' : createMenuItems()})
     
def game_delete(request, gameid=None):
  if gameid is not None:
    Game.objects.get(id=gameid).delete()    
  return HttpResponseRedirect('/admin/games/')
    