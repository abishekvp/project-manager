import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.http import JsonResponse
from app.decorators import login_required
from constants import constants as const

class MailServer:
    server = None
    server_host = ''
    port = ''
    username = ''
    password = ''
    from_email = ''
    
    @classmethod
    def login_server(cls, server, port, username, password, from_email):
        try:
            cls.server_host = server
            cls.port = port
            cls.username = username
            cls.password = password
            cls.from_email = from_email
            cls.server = smtplib.SMTP(cls.server_host, cls.port)
            cls.server.starttls()
            cls.server.login(cls.username, cls.password)
            return {'status': 200, 'message': 'Login successful'}
        except Exception as e:
            cls.server = None
            return {'status': 500, 'message': f'Login failed: {e}'}

    @classmethod
    def send_mail(cls, to_mail, subject, message):
        try:
            if cls.server is None:
                return {'status': 500, 'message': 'Server not configured.'}
            msg = MIMEMultipart()
            msg['From'] = cls.from_email
            msg['To'] = to_mail
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'html'))
            cls.server.sendmail(cls.from_email, to_mail, msg.as_string())
            return {'status': 200, 'message': 'Email sent successfully'}
        except Exception as e:
            return {'status': 500, 'message': f'Failed to send email: {e}'}

    @classmethod
    def quit_server(cls):
        if cls.server:
            cls.server.quit()
            cls.server = None

def send_project_assigned_mail(project, manager):
    manager_name = manager.first_name or manager.username
    context = const.project_assigned_mail_context(project, manager_name)
    mailserver = MailServer()
    result = mailserver.send_mail(to_mail=manager.email, subject=context['subject'], message=context['message'])
    return JsonResponse({'status': 200})