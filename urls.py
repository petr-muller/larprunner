from django.conf.urls.defaults import *
from django.contrib.auth.views import password_reset

urlpatterns = patterns('larprunner',  
  
  (r'^login/{0,1}$',        'users.views.login'),
  (r'^logout/{0,1}$',       'users.views.logout'),
  (r'^users/prefs/(?P<userid>\d{1,3})/{0,1}$', 'users.views.preferences'),
  
  (r'^badlogin/{0,1}$',     'users.views.login', {'bad' : True}),
  (r'^registration/{0,1}$', 'users.views.register'),
  (r'^users/activate/(?P<activation_key>[a-f0-9]{40})/{0,1}$', 'users.views.activate'),
  (r'^game/(?P<eventid>\d{1,3})/{0,1}$', 'events.views.event_app'),
  (r'^game/(?P<eventid>\d{1,3})/unregister/{0,1}$', 'events.views.event_unapp'),
  (r'^game/(?P<eventid>\d{1,3})/slots/{0,1}$', 'events.views.slots'),
  (r'^game/(?P<eventid>\d{1,3})/slots_change/{0,1}$', 'events.views.slots_change'),

  (r'^/{0,1}$',               'events.views.mainpage'),
  (r'^admin/{0,2}$',          'admin.events_views.overview'),
  (r'^admin/logout/{0,1}$',   'users.views.logout' ),
  (r'^admin/userland/{0,1}$', 'events.views.mainpage'),
  (r'^admin/users/{0,1}$',   'admin.users_views.list_users'),
  (r'^admin/users/reset/(?P<pid>\d+)/{0,1}', 'admin.users_views.admin_force_passwd_reset'),
  (r'^admin/users/sort_by_(?P<sort>[a-z_]+)/{0,1}', 'admin.users_views.list_users'),
  
  (r'^admin/games/{0,1}$', 'admin.games_views.administrate_games'),
  (r'^admin/games/(?P<gameid>new|\d{1,3})/{0,1}$', 'admin.games_views.game_modify'),
  (r'^admin/games/(?P<gameid>\d{1,3})/questions/{0,1}$', 'admin.games_views.game_modify', {'qmod':True}),
  (r'^admin/games/delete/(?P<gameid>\d{1,3})/{0,1}$', 'admin.games_views.game_delete'),
  
  (r'^admin/events/{0,1}$', 'admin.events_views.events'),  
  (r'^admin/events/(?P<type>(single|multi))/(?P<eventid>(new)|(\d{1,3}))/{0,1}$', 'admin.events_views.modify'),
  (r'^admin/events/(?P<type>(single|multi))/(?P<eventid>(\d{1,3}))/setstate/(?P<state>([A-Z]+))/{0,1}$', 'admin.events_views.set_state'),
  (r'^admin/events/(single|multi)/(?P<eventid>\d{1,3})/people/{0,1}$', 'admin.events_views.show_applied_people'),
  (r'^admin/events/(single|multi)/(?P<eventid>\d{1,3})/people/sort_by_(?P<sorted>[a-z]+)/{0,1}$', 'admin.events_views.show_applied_people'),
  (r'^admin/events/(single|multi)/(?P<eventid>\d{1,3})/people/cvsexport/{0,1}$', 'admin.events_views.show_applied_people', { 'cvsexport' : True }),
  (r'^admin/events/(?P<type>(single|multi))/(?P<eventid>\d{1,3})/regcreate/{0,1}$', 'admin.events_views.modify', {'regcreate' : True}),
  (r'^admin/events/multi/(?P<eventid>\d{1,3})/people/wslots/{0,1}$', 'admin.events_views.show_applied_people', {'slotted' : True}),
  (r'^admin/events/multi/(?P<eventid>\d{1,3})/people/wslots/cvsexport/{0,1}$', 'admin.events_views.show_applied_people', {'slotted' : True, 'cvsexport' : True}),
  (r'^admin/events/multi/(?P<eventid>\d{1,3})/slots/(?P<slotid>(new)|(\d{1,3}))/{0,1}$', 'admin.events_views.slot_modify'),
  (r'^admin/events/multi/(?P<eventid>\d{1,3})/slots/(?P<slotid>\d{1,3})/add/{0,1}$', 'admin.events_views.add_game_to_slot'),
  (r'^admin/events/multi/(?P<eventid>\d{1,3})/slots/(?P<slotid>\d{1,3})/delete/{0,1}$', 'admin.events_views.delete_slot'),
  (r'^admin/events/multi/(?P<eventid>\d{1,3})/slots/(?P<slotid>\d{1,3})/(?P<gameid>\d{1,3})/delete/{0,1}$', 'admin.events_views.delete_game_from_slot'),
  (r'^admin/events/multi/(?P<eventid>\d{1,3})/people_at_slots/{0,1}$', 'admin.events_views.show_applied_people_in_slots'),
  (r'^admin/events/multi/(?P<eventid>\d{1,3})/slot_details/(?P<slotid>\d{1,3})/{0,1}$', 'admin.events_views.slot_details'),
  (r'^admin/events/multi/(?P<eventid>\d{1,3})/people_action_slot/{0,1}$', 'admin.events_views.slotregistration_action'),
  (r'^admin/events/(single|multi)/(?P<eventid>\d{1,3})/people/action/{0,1}$', 'admin.events_views.people_action'),
  (r'^admin/questions/{0,1}$', 'admin.questions_views.questions'),
  (r'^admin/questions/(?P<queid>(new)|(\d{1,3}))/{0,1}$', 'admin.questions_views.question_edit'),
  
)


urlpatterns += patterns('',
                        (r'^styles/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/afri/Projects/larp-labs/larp-runner/larprunner/media'}),
                        (r'^passreset/{0,1}$', 'django.contrib.auth.views.password_reset', {'template_name' : 'passreset.html', 'email_template_name' : 'password_reset_email.html'}),
                        (r'^passreset/done/$', 'django.contrib.auth.views.password_reset_done', {'template_name' : 'password_reset_done.html'}),
                        (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {'template_name' : 'password_reset_confirm.html'}),
                        (r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete',{'template_name' : 'password_reset_complete.html'}),
                        (r'^(?P<path>(robots.txt)|(favicon.ico))$', 'django.views.static.serve', {'document_root': '/var/www/courtofmoravia/prihlaska/media'}),
                        (r'^passreset/{0,1}$', 'django.contrib.auth.views.password_reset', {'template_name' : 'passreset.html', 'email_template_name' : 'password_reset_email.html'}),                        
  )
