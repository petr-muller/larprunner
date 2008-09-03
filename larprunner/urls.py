from django.conf.urls.defaults import *

urlpatterns = patterns('larprunner',  
  
  (r'^login/{0,1}$',        'users.views.login'),
  (r'^logout/{0,1}$',       'users.views.logout'),
  (r'^badlogin/{0,1}$',     'users.views.login', {'bad' : True}),
  (r'^registration/{0,1}$', 'users.views.register'),
  (r'^users/activate/(?P<activation_key>[a-f0-9]{40})/{0,1}$', 'users.views.activate'),
  
  
  (r'^/{0,1}$',               'events.views.mainpage'),
  (r'^admin/{0,1}$',          'admin.events.overview'),
  (r'^admin/logout/{0,1}$',   'users.views.logout' ),
  (r'^admin/userland/{0,1}$', 'events.views.mainpage'),
  
  (r'^admin/games/{0,1}$', 'admin.games.administrate_games'),
  (r'^admin/games/(?P<gameid>new|\d{1,3})/{0,1}$', 'admin.games.game_modify'),
  (r'^admin/games/delete/(?P<gameid>\d{1,3})/{0,1}$', 'admin.games.game_delete'),
  
  (r'^admin/events/{0,1}$', 'admin.events.events'),  
  (r'^admin/events/(?P<type>(single|multi))/(?P<eventid>(new)|(\d{1,3}))/{0,1}$', 'admin.events.modify'),
  
  (r'^admin/events/multi/(?P<eventid>\d{1,3})/slots/(?P<slotid>(new)|(\d{1,3}))/{0,1}$', 'admin.events.slot_modify'),
  (r'^admin/events/multi/(?P<eventid>\d{1,3})/slots/(?P<slotid>\d{1,3})/add/{0,1}$', 'admin.events.add_game_to_slot'),
)

urlpatterns += patterns('',
                        (r'^styles/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/afri/Projects/larp-labs/larp-runner/larprunner/media'}),
  )