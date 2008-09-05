# This Python file uses the following encoding: utf-8

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from manipulation import my_login_required, createMenuItems, my_admin_required
from larprunner.questions.models import Question

@my_admin_required
def questions(request):
  return render_to_response("admin/questions.html",
                            { 'menuitems' : createMenuItems('questions'),
                              'questions' : Question.objects.all(),                              
                              'user'      : request.user,
                              'title'     : "Otázky"  }
                            )