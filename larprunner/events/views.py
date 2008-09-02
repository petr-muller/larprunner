# Create your views here.
from django.shortcuts import render_to_response
from larprunner.admin.manipulation import my_login_required

def mainpage(request):
  if request.user.is_authenticated():
    user = request.user
  else:
    user = None
  print user
  return render_to_response("events/mainpage.html",
                            {'user' : user} )
   