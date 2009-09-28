from django.db import models

# Create your models here.

class HubMessage:
  def __init__(self, id, payload):
    self.id = id
    self.payload = payload

  def getId(self):
    return self.id

  def getData(self, key):
    return self.payload[key]

  def __unicode__(self):
    return "Message '%s': [%s]" % (self.id, self.payload)

class Singleton(type):
  """This is a singleton"""
  def __init__(self, name, bases, dict):
    super(Singleton, self).__init__(name, bases, dict)
    self.instance = None

  def __call__(self, *args, **kw):
    if self.instance is None:
      self.instance = super(Singleton, self).__call__(*args, **kw)

    return self.instance

class Hub:
    __metaclass__ = Singleton

    def initialize(self):
      try:
        self.notify_table
      except AttributeError:
        self.notify_table = {}

    def subscribe(self, notify, event):
      self.initialize()
      if not self.notify_table.has_key(event):
        self.notify_table[event] = []
      if notify not in self.notify_table[event]:
        self.notify_table[event].append(notify)
        print "%s has subscribed to %s" % (str(notify), event)

    def unsubscribe(self, notify, event):
      self.initialize()
      if self.notify_table.has_key(event) and notify in self.notify_table[event]:
        self.notify_table[event].remove(notify)

    def deliver(self, id, data):
      self.initialize()
      if self.notify_table.has_key(id):
        message = HubMessage(id, data)
        for observer in self.notify_table[id]:
          observer(message)
