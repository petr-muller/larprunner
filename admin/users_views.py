# This Python file uses the following encoding: utf-8

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from manipulation import my_login_required, createMenuItems, my_admin_required
from larprunner.users.models import Player
from larprunner.tables.models import MightyTable, SimpleCell, URLCell

@my_admin_required
def list_users(request, sort):
  if sort is None:
    sort = "UID"
  headers = [u"Login", u"Jméno", u"Nick", u"Mail", u"Telefon", u"Narození", u"UID", u"Heslo"]
  table = MightyTable(headers)
  for player in Player.objects.select_related():
    record = {}
    record[u"Login"]     = SimpleCell(player.getLogin())
    record[u"Jméno"]     = SimpleCell(player.getFullName(nick=False))
    record[u"Nick"]      = SimpleCell(player.getNick())
    record[u"Mail"]      = SimpleCell(player.getMail())
    record[u"Telefon"]   = SimpleCell(player.getPhone())
    record[u"Narození"]  = SimpleCell(player.getBirth())
    record[u"UID"]       = SimpleCell(player.getUID())
    record[u"Heslo"]     = URLCell("reset/%s/" % player.getID(), "reset")
    table.addRecord(record)
  table.sort(sort)
  return render_to_response("admin/users.html",
                            { 'menuitems' : createMenuItems('users'),
                              'table'     : table,
                              'user'      : request.user,
                              'title'     : "Uživatelé"  }
                            )
@my_admin_required
def admin_force_passwd_reset(request, pid):
  player = Player.objects.get(id=pid)
  player.force_reset()
  return HttpResponseRedirect("/admin/users/")
