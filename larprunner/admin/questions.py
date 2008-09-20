# This Python file uses the following encoding: utf-8

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from manipulation import my_login_required, createMenuItems, my_admin_required
from larprunner.questions.models import Question
from larprunner.questions.forms import CreateQuestionForm

@my_admin_required
def questions(request):
  return render_to_response("admin/questions.html",
                            { 'menuitems' : createMenuItems('questions'),
                              'questions' : Question.objects.all(),                              
                              'user'      : request.user,
                              'title'     : "Otázky"  }
                            )

@my_admin_required
def question_edit(request, queid):
  if request.method == 'POST':
    form = CreateQuestionForm(request.POST)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect('/admin/questions')
  else:
    form = CreateQuestionForm()
    if queid != "new":
      form.loadValues(queid)
    return render_to_response("admin/questionform.html",
                            { 'menuitems' : createMenuItems('questions'),
                              'user'      : request.user,
                              'title'     : 'Změnit otázku',
                              'form'      : form})

