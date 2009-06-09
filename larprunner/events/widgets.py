from django.forms.widgets import RadioInput, RadioFieldRenderer, RadioSelect
from django.forms.util import smart_unicode
from itertools import chain

class RadioInputWithDisable(RadioInput):
    "An object used by RadioFieldRenderer that represents a single <input type='radio'>."
    def __init__(self, name, value, attrs, choice, index):
        self.name, self.value = name, value
        self.attrs = attrs
        self.choice_value = smart_unicode(choice[0])
        self.choice_label = smart_unicode(choice[1])
        if len(choice) > 2:
          if choice[2] == "disabled":
            self.attrs["disabled"] = "disabled"
        self.index = index
    def __unicode__(self):
      disabled=""
      if self.attrs.get("disabled", None) == "disabled":
        disabled=' style="color: #aa2200;"'
      
      return u'<label%s>%s %s</label>' % ( disabled, self.tag(), self.choice_label)
    
class RadioFieldRendererWithDisable(RadioFieldRenderer):
    "An object used by RadioSelect to enable customization of radio widgets."
    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield RadioInputWithDisable(self.name, self.value, self.attrs.copy(), choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx] # Let the IndexError propogate
        return RadioInputWithDisable(self.name, self.value, self.attrs.copy(), choice, idx)
  
class RadioSelectWithDisable(RadioSelect):
  def render(self, name, value, attrs=None, choices=()):
    "Returns a RadioFieldRenderer instance rather than a Unicode string."
    if value is None: value = ''
    str_value = smart_unicode(value) # Normalize to string.
    attrs = attrs or {}
    return RadioFieldRendererWithDisable(name, str_value, attrs, list(chain(self.choices, choices)))
    
