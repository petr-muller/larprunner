from larprunner.hub.models import Hub
from models import Mailer

initialize = Hub()
mailer = Mailer(initialize)
mailer.hook("player has unsubscribed from event")