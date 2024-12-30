from django.apps import AppConfig
from django.db.models.signals import post_migrate
from constants import constants as const
import atexit

        
class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    def ready(self):
        post_migrate.connect(create_default_groups, sender=self)
        config_mail_server()
        atexit.register(on_server_stop)

def create_default_groups(sender, **kwargs):
    from django.contrib.auth.models import Group
    Group.objects.get_or_create(name=const.LEAD)
    Group.objects.get_or_create(name=const.PEER)
    Group.objects.get_or_create(name=const.MANAGER)
    Group.objects.get_or_create(name=const.VENDOR)
    Group.objects.get_or_create(name=const.ADMINISTER)

def config_mail_server():
    from .mail_server import MailServer
    from .models import MailServer as MailModel
    mailmodel = MailModel.objects.first()
    if mailmodel:
        mailserver = MailServer()
        mailserver.login_server(mailmodel.server, mailmodel.port, mailmodel.username, mailmodel.password, mailserver.from_email)

def on_server_stop():
    from .mail_server import MailServer
    mailserver = MailServer()
    if mailserver.server:
        mailserver.server.quit()