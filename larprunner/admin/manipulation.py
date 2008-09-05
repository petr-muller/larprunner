# This Python file uses the following encoding: utf-8
from django.contrib.auth.decorators import user_passes_test

my_login_required = user_passes_test(lambda u: u.is_authenticated(), login_url='/login/')
my_admin_required = user_passes_test(lambda u: u.is_authenticated() and u.is_staff, login_url='/login/')

class menuitem:
  path = ""
  screen = ""
  active = 1
  def __init__(self, path, screen, active):
    self.path = path
    self.screen = screen
    self.active = active

def createMenuItems(active=None):
  ret = []
  ret.append(menuitem("questions",u"Otázky", 0))
  ret.append(menuitem("games",    u"Hry", 0))
  ret.append(menuitem("events",   u"Akce", 0))
  ret.append(menuitem("",         u"Overview", 0))
  ret.append(menuitem("userland", u"Uživatelský pohled", 0))
  ret.append(menuitem("logout",   u"Odhlásit", 0))
  
  for item in range(len(ret)):
    if ret[item].path == active:
      ret[item].active = 1
  
  return ret