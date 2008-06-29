# This Python file uses the following encoding: utf-8
from models import Game
from django.newforms import form_for_model, BaseForm, ValidationError

class intNewGameForm(BaseForm):
  def clean_roles(self):
    roles = self.clean_data.get('roles', '')
    m = self.clean_data.get('roles_male','0')
    f = self.clean_data.get('roles_female','0')
    b = self.clean_data.get('roles_both','0')
    if int(roles) != int(m) + int(f) + int(b):
      raise ValidationError("Počet rolí se musí rovnat součtu mužských, ženských a obecných rolí")
    return roles

NewGameForm = form_for_model(Game, form=intNewGameForm)