import smtplib
from email.mime.text import MIMEText


smtp_ssl_host = 'poczta.o2.pl'
smtp_ssl_port = 465

username = 'mailwno@o2.pl'
password = 'kurwa123'

from_addr = 'mailwno@o2.pl'
to_addrs = ['kpilarski21@gmail.com']

message = MIMEText('to jest wiadomosc testowa')
message['subject'] = 'test'
message['from'] = from_addr
message['to'] = ', '.join(to_addrs)

server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)

server.login(username, password)
server.sendmail(from_addr, to_addrs, message.as_string())
server.quit()
