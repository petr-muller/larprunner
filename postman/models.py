from django.db import models
from hub.models import Hub, Singleton

class Mailer:
  __metaclass__ = Singleton

  def __init__(self, hub):
    self.hub = hub

  def hook(self, event):
    self.hub.subscribe(self.notify, event)

  def notify(self, message):
    print "I would send a message for %s" % message
