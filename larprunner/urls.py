from django.conf.urls.defaults import *

urlpatterns = patterns('larprunner',
  (r'^admin/login/{0,1}$', 'admin.views.admlogin'),
  (r'^admin/signup/{0,1}$', 'admin.views.signup'),
  (r'^admin/hello/{0,1}$', 'admin.views.hello'),
  (r'^admin/start/{0,1}$', 'admin.views.games'),
  (r'^admin/games/{0,1}$', 'admin.views.games'),
  (r'^admin/games/new/{0,1}$', 'admin.views.game_modify'),
  (r'^admin/games/(?P<gameid>\d{1,3})/{0,1}$', 'admin.views.game_modify'),
  (r'^admin/games/delete/(?P<gameid>\d{1,3})/{0,1}$', 'admin.views.game_delete'),
)
