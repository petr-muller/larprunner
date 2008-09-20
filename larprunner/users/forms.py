# This Python file uses the following encoding: utf-8
from django import newforms as forms
from django.core.validators import alnum_re
from django.contrib.auth.models import User
import re

from users.models import RegistrationProfile

# I put this on all required fields, because it's easier to pick up
# on them with CSS or JavaScript if they have a class of "required"
# in the HTML. Your mileage may vary. If/when Django ticket #3515
# lands in trunk, this will no longer be necessary.
attrs_dict = { 'class': 'required' }

GENDER_CHOICES = (
    ('Male', 'Muž'),
    ('Female', 'Žena'),    
)

YEAR_REGEXP=re.compile("\d{4}")
PHONE_REGEXP=re.compile("\+\d{12}")
def _(msg):
  return msg

class RegistrationForm(forms.Form):
    """
    Form for registering a new user account.
    
    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.
    
    Subclasses should feel free to add any additional validation they
    need, but should either preserve the base ``save()`` or implement
    a ``save()`` which accepts the ``profile_callback`` keyword
    argument and passes it through to
    ``RegistrationProfile.objects.create_inactive_user()``.
    
    """
    username = forms.CharField(max_length=30,
                               widget=forms.TextInput(attrs=attrs_dict),
                               label=_(u'Login'))
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_(u'e-mail'))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_(u'Heslo'))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_(u'Ověření hesla'))
    
    name = forms.CharField(max_length=30,
                           widget=forms.TextInput(attrs=attrs_dict),
                           label=_(u'Jméno'))
    surname = forms.CharField(max_length=30,
                           widget=forms.TextInput(attrs=attrs_dict),
                           label=_(u'Příjmení'))
    nick  = forms.CharField(max_length=30,
                            required=False)
    year_of_birth = forms.IntegerField(label=_(u'Rok narození'))
    phone = forms.CharField(max_length=13, min_length=13,
                            widget=forms.TextInput(attrs=attrs_dict),
                            label=_(u'Telefon (ve tvaru +420 111 222 333)'))
    gender = forms.ChoiceField(choices=GENDER_CHOICES,
                                label=_(u'Pohlaví'))

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.        
        """
        if not alnum_re.search(self.clean_data['username']):
            raise forms.ValidationError(_(u'Uživatelské jméno může obsahovat pouze písmena, číslice a podtržítko'))
        
        
        try:
            user = User.objects.get(username__iexact=self.clean_data['username'])
        except User.DoesNotExist:
            return self.clean_data['username']
        raise forms.ValidationError(_(u'Toto uživatelské jméno už je zabráno'))
    
    def clean_year_of_birth(self):
      """
      Validate the correctness of birth year
      """
      
      if not YEAR_REGEXP.match(str(self.clean_data['year_of_birth'])):
        raise forms.ValidationError(_(u'Špatně zadaný rok'))
      return self.clean_data['year_of_birth']
    
    def clean_phone(self):
      """
      Validate the correctness of phone
      """      
      if not PHONE_REGEXP.match(self.clean_data['phone'].replace(' ','')):
        raise forms.ValidationError(_(u'Špatně zadané telefonní číslo'))
      return self.clean_data['phone'].replace(' ','')
      
    def clean(self):
        """
        Verify that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        
        """
        if 'password1' in self.clean_data and 'password2' in self.clean_data:
            if self.clean_data['password1'] != self.clean_data['password2']:
                raise forms.ValidationError(_(u'Rozdílná hesla'))
        return self.clean_data
    
    def save(self, profile_callback=None):
        """
        Create the new ``User`` and ``RegistrationProfile``, and
        returns the ``User``.
        
        This is essentially a light wrapper around
        ``RegistrationProfile.objects.create_inactive_user()``,
        feeding it the form data and a profile callback (see the
        documentation on ``create_inactive_user()`` for details) if
        supplied.
        
        """
        new_user = RegistrationProfile.objects.create_inactive_user(username=self.clean_data['username'],
                                                                    password=self.clean_data['password1'],
                                                                    email=self.clean_data['email'],
                                                                    name = self.clean_data['name'],
                                                                    surname = self.clean_data['surname'],
                                                                    year = self.clean_data['year_of_birth'],
                                                                    phone = self.clean_data['phone'],
                                                                    gender = self.clean_data['gender'],
                                                                    nick = self.clean_data['nick'])
        return new_user
