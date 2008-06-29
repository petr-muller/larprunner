from django.contrib.auth.decorators import user_passes_test

my_login_required = user_passes_test(lambda u: u.is_authenticated(), login_url='/admin/login/')

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
  ret.append(menuitem("games", "Hry", 0))
  ret.append(menuitem("events", "Akce", 0))
  ret.append(menuitem("overview", "Overview", 0))        
  
  for item in range(len(ret)):
    if ret[item].path == active:
      ret[item].active = 1
  
  return ret