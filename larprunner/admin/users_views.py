# This Python file uses the following encoding: utf-8

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from manipulation import my_login_required, createMenuItems, my_admin_required
from larprunner.users.models import Player

@my_admin_required
def list_users(request):
  return render_to_response("admin/users.html",
                            { 'menuitems' : createMenuItems('users'),
                              'players' : Player.objects.all(),
                              'user'      : request.user,
                              'title'     : "Uživatelé"  }
                            )
@my_admin_required
def admin_force_passwd_reset(request, pid):
  player = Player.objects.get(id=pid)
  player.force_reset()
  return HttpResponseRedirect("/admin/users/")
