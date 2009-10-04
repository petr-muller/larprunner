from django.db import models
import locale

# Create your models here.
class Cell():
  def isSafe(self):
    return False

class SimpleCell(Cell):
  def __init__(self, value):
    self.value = value

  def asCode(self):
    return unicode(self.value)

  def __unicode__(self):
    return self.asCode()

  def __str__(self):
    return self.asCode()

class URLCell(Cell):
  def __init__(self, url, label=None):
    if label is None:
      label = url
    self.url = url
    self.label = label

  def asCode(self):
    return u'<a href="%s">%s</a>' % (self.url, self.label)

  def __unicode__(self):
    return self.asCode()

  def isSafe(self):
    return True

  def __str__(self):
    return self.asCode()

class CheckerCell(Cell):
  def __init__(self, id, prefix="magic"):
    self.id = id
    self.prefix = prefix

  def asCode(self):
    return u'<input type="checkbox" name="%s%s" />' % (self.prefix, self.id)

  def __unicode__(self):
    return self.asCode()

  def isSafe(self):
    return True

  def __str__(self):
    return self.asCode()

class MightyTable:
  def __init__(self, headers):
    self.headers = headers
    self.records = []

  def addRecord(self, new_record):
    record = []
    for key in self.headers:
      record.append(new_record.get(key))
    self.records.append(record)

  def sort(self, column, reverse=False):
    index = self.headers.index(column)
    self.records.sort(cmp=lambda x,y: locale.strcoll(unicode(x[index]), unicode(y[index])))
    if reverse:
      self.records.reverse()