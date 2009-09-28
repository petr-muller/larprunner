# This Python file uses the following encoding: utf-8
from django.db import models
from hub.models import Hub, Singleton
import settings

class Mailer:
  __metaclass__ = Singleton

  def __init__(self, hub):
    self.hub = hub
    self.catalogue = { "player has unsubscribed from event" : self.eventPlayerUnsub,
                       "player has subscribed to event" : self.eventPlayerSub }
    self.FROM = settings.DEFAULT_FROM_EMAIL

  def hook(self, event):
    self.hub.subscribe(self.notify, event)

  def notify(self, message):
    try:
      method = self.catalogue[message.getId()]
      method(message)
    except KeyError:
      print "I don't know such message"

  def sendMail(self, subject, message, recipients):
    from django.core.mail import send_mail
    send_mail(subject, message, self.FROM, recipients)

  def eventPlayerUnsub(self, message):
    event = message.getData("event")
    subject = u"[Larprunner] %s: hráč %s se odhlásil" % (event.getName(), message.getData("player"))
    message = u"[Larprunner] %s: hráč %s se odhlásil" % (event.getName(), message.getData("player"))
    recipients = event.getAdminRecipients()
    if recipients:
      self.sendMail(subject, message, recipients)

  def eventPlayerSub(self, message):
    pass