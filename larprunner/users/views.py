# This Python file uses the following encoding: utf-8

from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from larprunner.admin.manipulation import my_login_required
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from larprunner.users.forms import RegistrationForm, PreferencesForm
from larprunner.users.models import RegistrationProfile


def login(request,
          next='/',
          bad=None,
          template_name = "login-screen.html"):
  if request.method == 'POST':
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    next     = request.POST.get('next', '/')
    if None not in (username, password):
      user = authenticate(username=username, password=password)
      if user is not None and user.is_active:     
        django_login(request, user)          
        return HttpResponseRedirect(next)
          
    return HttpResponseRedirect('/badlogin/')
  else:
    if bad is not None:
      msg = "Přihlášení se nezdařilo. Zkontrolujte zadávané jméno a heslo"
    else:
      msg = None
    return render_to_response(template_name,
                              {'next': next, 'msg' : msg, 'title' : "Login"})
@my_login_required
def logout(request):
  django_logout(request)
  return HttpResponseRedirect('/')

def activate(request, activation_key,
             template_name='users/activation.html'):
    """
    Activate a ``User``'s account from an activation key, if their key
    is valid and hasn't expired.  
    """
    
    activation_key = activation_key.lower() # Normalize before trying anything with it
    account = RegistrationProfile.objects.activate_user(activation_key)
        
    return render_to_response(template_name,
                              { 'account': account,
                                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                                'title' : 'Aktivace' })

def register(request, success_url=None,
             form_class=RegistrationForm, profile_callback=None,
             template_name='users/registration.html'):
    """
    Allow a new user to register an account.
    """
    
    if request.method == 'POST':
        form = form_class(data=request.POST)
        if form.is_valid():
            new_user = form.save(profile_callback=profile_callback)
            # success_url needs to be dynamically generated here; setting a
            # a default value using reverse() will cause circular-import
            # problems with the default URLConf for this application, which
            # imports this file.
            return render_to_response('users/reg_success.html')
    else:
        form = form_class()
    
    return render_to_response(template_name,
                              { 'form': form, 'title' : 'Registrace'})

def preferences(request, userid):
  form = PreferencesForm()
  print form.fields["password1"].required
  if request.method == 'POST':
    form = PreferencesForm(request.POST)
    form.fields["password1"].required = False
    form.fields["password2"].required = False
    if form.is_valid():
      form.save()
  else:
    form.load(request.user)

  return render_to_response('users/preferences.html',
                            { 'form' : form, 'title' : u'Uživatel %s' % request.user.username })