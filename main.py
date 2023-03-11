import smtplib, ssl

sender_addr = 'smtpwno@wp.pl'
sender_password = 'haselko123'
receiver_addr = 'kpilarski21@gmail.com'
wp = ('smtp.wp.pl', 587)

# if __name__ == '__main__':
try:
    with smtplib.SMTP(wp[0], wp[1]) as smtp:
        # smtp.ehlo()
        smtp.login(sender_addr, sender_password)

        subject = 'subject'
        body = 'body'
        msg = f'Subject: {subject}\n\n{body}'

        smtp.sendmail(sender_addr, receiver_addr, msg)
except:
    print('error')
