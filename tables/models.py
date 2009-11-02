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

  def asPlain(self):
    return self.asCode()

  def getValue(self):
    return self.value

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

  def asPlain(self):
    return self.url

  def getValue(self):
    return self.url

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

  def asPlain(self):
    return unicode(self.id)

  def getValue(self):
    return self.id

class MightyTable:
  def sortAsStrings(self, index):
    self.records.sort(cmp=lambda x,y: cmp(unicode(x[index].getValue()).lower(), unicode(y[index].getValue()).lower()))

  def sortAsNumbers(self, index):
    self.records.sort(cmp=lambda x,y: cmp(x[index].getValue(), y[index].getValue()))

  def setNumeric(self, record):
    self.numeric.append(record)

  def __init__(self, headers):
    self.headers = headers
    self.records = []
    self.numeric = []

  def addRecord(self, new_record):
    record = []
    for key in self.headers:
      record.append(new_record.get(key))
    self.records.append(record)

  def sort(self, column, reverse=False):
    index = self.headers.index(column)
    if column in self.numeric:
      self.sortAsNumbers(index)
    else:
      self.sortAsStrings(index)

    if reverse:
      self.records.reverse()

  def asCSV(self, quote=u'"', separator=u","):
    headerline = separator.join([ '%s%s%s' % (quote, header, quote) for header in self.headers ])
    rows = [headerline]
    for row in self.records:
      rowline = separator.join([ '%s%s%s' % (quote, item.asPlain(), quote) for item in row])
      rows.append(rowline)

    return "\n".join(rows)



