from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import user_passes_test 
from django.contrib.auth import authenticate, login
my_login_required = user_passes_test(lambda u: u.is_authenticated(), login_url='/admin/login/')

def signup(request):
  username = request.POST['username']
  password = request.POST['password']
  if None not in (username, password):
    user = authenticate(username=username, password=password)
    if user is not None:
      if user.is_active:
        login(request, user)
        next = request.GET['next']
        if next is None:
          next = "/admin/start/"
        return HttpResponseRedirect(next)
      else:
        return HttpResponseRedirect('/admin/login/')
  else:
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
