from django import template

register = template.Library()

@register.filter
def in_list(value,arg):
  print "%s in %s" % (value, arg)
  return value in arg
