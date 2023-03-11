import smtplib
import imaplib
import email
import os

smtp_addr = 'smtp.gmail.com'
smtp_port = 465
imap_addr = 'imap.gmail.com'
imap_port = 993

username = 'smtpwno@gmail.com'
password = 'ygsygzttdqbcekjp'
auto_rec_addr = 'kpilarski21@gmail.com'


def send_email(mess, receiver):
    # message2send =
    mess['To'] = receiver
    try:
        with smtplib.SMTP_SSL(smtp_addr, smtp_port) as server:
            server.login(username, password)
            server.send_message(mess)
            return True
    except:
        return False


def get_emails(messages):
    with imaplib.IMAP4_SSL(imap_addr, imap_port) as server:
        server.login(username, password)
        server.select('Inbox')

        _, msg_ids_coded = server.search(None, 'ALL')
        msg_ids = msg_ids_coded[0].split()

        if len(messages) == 0:
            for msg_id in msg_ids:
                _, data = server.fetch(msg_id, "(RFC822)")
                mes = email.message_from_bytes(data[0][1])
                messages.append([int(msg_id), mes])
            return messages
        elif int(msg_ids[-1]) == messages[-1][0]:
            return messages
        else:
            messages.clear()
            for msg_id in msg_ids:
                _, data = server.fetch(msg_id, "(RFC822)")
                mes = email.message_from_bytes(data[0][1])
                messages.append([int(msg_id), mes])
            return messages


def get_content(message):
    all_mes = ''
    for part in message.walk():
        if part.get_content_type() == "text/plain":
            message_parted = part.as_string().split('\n')
            # print(message_parted[2:])
            for line in message_parted[2:]:
                all_mes += line
                all_mes += '\n'
    return all_mes


def mail2terminal(messages):
    for message in messages:
        print("Message ID: ", message[0])
        print("Subject: ", message[1].get('Subject'))
        msg_content = get_content(message[1])
        print("Content: ", msg_content, '\n')
        # print(type(msg[1]))  ->  <class 'email.message.Message'>


def filter_msgs():
    pass


def auto_responder(messages):
    with smtplib.SMTP_SSL(smtp_addr, smtp_port) as user:
        user.login(username, password)
        for message in messages:
            to_respond = email.message.EmailMessage()
            to_respond['Subject'] = message[1]['Subject']
            to_respond['From'] = username
            to_respond.set_content(get_content(message[1]))
            to_respond['To'] = auto_rec_addr
            user.send_message(to_respond)


if __name__ == '__main__':
    to_send = email.message.EmailMessage()
    to_send['Subject'] = 'Email subject'
    to_send['From'] = username
    to_send.set_content('Body of email')
    send_email(to_send, auto_rec_addr)

    messages = []
    while True:
        num_of_new_mes = len(messages)
        messages = get_emails(messages)
        num_of_new_mes -= len(messages)
        if not num_of_new_mes == 0:
            os.system('clear')
            mail2terminal(messages)
            auto_responder(messages[num_of_new_mes:])
            # for message in messages[num_of_new_mes:]:
            #     send_email(message[1], auto_rec_addr)



