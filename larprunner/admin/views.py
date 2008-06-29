from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login
from manipulation import my_login_required, createMenuItems
from models import Game
from forms import NewGameForm

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

def game_new(request):
  if request.method == 'POST':
    form = NewGameForm(request.POST)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect('/admin/games/')
  else:
    form = NewGameForm()
  return render_to_response('admin/gameform.html', {'form': form })