from django.conf.urls.defaults import *

urlpatterns = patterns('',
  (r'^admin/login/{0,1}$', 'larprunner.admin.views.admlogin'),
  (r'^admin/signup/{0,1}$', 'larprunner.admin.views.signup'),
  (r'^admin/hello/{0,1}$', 'larprunner.admin.views.hello'),
  (r'^admin/start/{0,1}$', 'larprunner.admin.views.games'),
  (r'^admin/games/{0,1}$', 'larprunner.admin.views.games'),
  (r'^admin/games/new/{0,1}$', 'larprunner.admin.views.game_new'),
)
