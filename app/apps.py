from django.apps import AppConfig
from django.db.models.signals import post_migrate
from constants import constants as const

def create_default_groups(sender, **kwargs):
    from django.contrib.auth.models import Group
    Group.objects.get_or_create(name=const.LEAD)
    Group.objects.get_or_create(name=const.PEER)
    Group.objects.get_or_create(name=const.MANAGER)

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    def ready(self):
        from .mail_server import MailServer
        from .models import MailServer as MailModel
        mailmodel = MailModel.objects.first()
        if mailmodel:
            mailserver = MailServer()
            mailserver.login_server(mailmodel.server, mailmodel.port, mailmodel.username, mailmodel.password, mailserver.from_email)
        post_migrate.connect(create_default_groups, sender=self)