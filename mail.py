import smtplib
from email.mime.text import MIMEText


class Mail:
    def __init__(self, smtp_server, smtp_port, smtp_username, smtp_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password

    def send_mail(self, data, mail,from_email = 'adm@lynx-cargo.com'):
        to_email = mail
        msg = MIMEText(data[1])

        msg['Subject'] = data[0]

        with smtplib.SMTP(f"{self.smtp_server}:{self.smtp_port}") as smtp:
            try:
                smtp.starttls()
                smtp.login(self.smtp_username, self.smtp_password)
                smtp.sendmail(from_email, to_email, msg.as_string())
            except Exception as e:
                print(f'Failed to send mail to {mail} from {from_email}, error: {e}')
                return False
            print(f"Sent mail to {mail} about {data[0]} from {from_email}")
        return True
