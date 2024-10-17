import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
                return {'status': 500, 'message': 'Server not logged in. Please login first.'}

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