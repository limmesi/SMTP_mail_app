from gensim.models import KeyedVectors
from PySide6.QtWidgets import *
from bs4 import BeautifulSoup
import requests
import smtplib
import imaplib
import email
import sys

smtp_addr = 'smtp.gmail.com'
smtp_port = 465
imap_addr = 'imap.gmail.com'
imap_port = 993

username = 'smtpwno@gmail.com'
password = 'ygsygzttdqbcekjp'
auto_rec_addr = 'kpilarski21@gmail.com'


class EmailClient(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Email Client')
        self.showMaximized()
        self.messages = []
        # Create UI widgets
        self.inbox_widget = QTextEdit()
        self.right_widget = QWidget()
        self.left_widget = QWidget()
        self.to_label = QLabel("To:")
        self.to_input = QLineEdit()
        self.subject_label = QLabel("Subject:")
        self.subject_input = QLineEdit()
        self.body_label = QLabel("Body:")
        self.label_filter_box = QLabel('Filter mails via keyword: ')
        self.input_filter_box = QLineEdit()
        self.create_account_label = QLabel("To create Google account fill the form bellow: ")
        self.create_account_username = QLineEdit()
        self.create_account_password = QLineEdit()
        self.create_account_button = QPushButton("Create account")

        self.content_of_mail_input = QTextEdit()
        self.body_input = QTextEdit()
        self.send_button = QPushButton("Send")
        self.show_email_button = QPushButton("Show mails")
        self.receive_mails_button = QPushButton("Download mails")
        self.filter_mails_on_keyword = QPushButton("Filter mails on the keyword")

        self.right_layout = QVBoxLayout()
        self.left_layout = QVBoxLayout()
        self.to_layout = QHBoxLayout()
        self.subject_layout = QHBoxLayout()
        self.body_layout = QVBoxLayout()
        self.input_layout = QHBoxLayout()
        self.content_of_mail_layout = QVBoxLayout()
        self.main_layout = QHBoxLayout()

        self.to_layout.addWidget(self.to_label)
        self.to_layout.addWidget(self.to_input)
        self.subject_layout.addWidget(self.subject_label)
        self.subject_layout.addWidget(self.subject_input)
        self.body_layout.addWidget(self.body_label)
        self.body_layout.addWidget(self.body_input)
        self.left_layout.addWidget(self.receive_mails_button)
        self.left_layout.addWidget(self.show_email_button)
        self.left_layout.addWidget(self.inbox_widget)
        self.left_layout.addWidget(self.create_account_label)
        self.left_layout.addWidget(self.create_account_username)
        self.left_layout.addWidget(self.create_account_password)
        self.left_layout.addWidget(self.create_account_button)
        self.right_layout.addLayout(self.to_layout)
        self.right_layout.addLayout(self.subject_layout)
        self.right_layout.addLayout(self.body_layout)
        self.right_layout.addWidget(self.send_button)
        self.right_layout.addLayout(self.input_layout)
        self.right_layout.addLayout(self.content_of_mail_layout)
        self.right_layout.addWidget(self.label_filter_box)
        self.right_layout.addWidget(self.input_filter_box)
        self.right_layout.addWidget(self.filter_mails_on_keyword)
        self.right_widget.setLayout(self.right_layout)
        self.left_widget.setLayout(self.left_layout)
        self.main_layout.addWidget(self.left_widget)
        self.main_layout.addWidget(self.right_widget)

        main_widget = QWidget()
        main_widget.setLayout(self.main_layout)
        self.setCentralWidget(main_widget)

        self.send_button.clicked.connect(self.send_email)
        self.show_email_button.clicked.connect(self.mail2gui)
        self.receive_mails_button.clicked.connect(self.get_emails)
        self.filter_mails_on_keyword.clicked.connect(self.filter_msgs)
        self.create_account_button.clicked.connect(self.create_gmail_account)

    def send_email(self):
        message2send = email.message.EmailMessage()
        message2send['Subject'] = self.subject_input.text()
        message2send['To'] = self.to_input.text()
        message2send['From'] = username
        message2send.set_content(self.body_input.toPlainText())
        try:
            with smtplib.SMTP_SSL(smtp_addr, smtp_port) as server:
                server.login(username, password)
                server.send_message(message2send)
        except Exception as e:
            print(e)
        self.subject_input.clear()
        self.to_input.clear()
        self.body_input.clear()
        print("EMAIL SENT")

    def auto_responder(self, mails):
        try:
            with smtplib.SMTP_SSL(smtp_addr, smtp_port) as server:
                server.login(username, password)
                for _, mail in mails:
                    mes2send = email.message.EmailMessage()
                    mes2send['Subject'] = "Automatic Respond"
                    mes2send['To'] = mail['From']
                    mes2send['From'] = username
                    mes2send.set_content("auto respond body")
                    server.send_message(mes2send)
                print("AUTO RESPONDER END")
        except Exception as e:
            print(e)

    def get_emails(self):
        with imaplib.IMAP4_SSL(imap_addr, imap_port) as server:
            server.login(username, password)
            server.select('Inbox')

            _, msg_ids_coded = server.search(None, 'ALL')
            msg_ids = msg_ids_coded[0].split()

            if len(self.messages) == 0:
                for msg_id in msg_ids:
                    _, data = server.fetch(msg_id, "(RFC822)")
                    mes = email.message_from_bytes(data[0][1])
                    self.messages.append([int(msg_id), mes])
            elif len(msg_ids) > len(self.messages):
                new_msgs = []
                for msg_id in msg_ids[len(self.messages):]:
                    _, data = server.fetch(msg_id, "(RFC822)")
                    mes = email.message_from_bytes(data[0][1])
                    new_msgs.append([int(msg_id), mes])
                    print(type(mes))
                self.auto_responder(new_msgs)
                # self.auto_resend(new_msgs)
                self.messages = new_msgs + self.messages
        print("EMAILS DOWNLOADED")

    def get_content(self, message):
        all_mes = ''
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                message_parted = part.as_string().split('\n')
                # print(message_parted[2:])
                for line in message_parted[2:]:
                    all_mes += line
                    all_mes += '\n'
        return all_mes

    def mail2gui(self):
        self.inbox_widget.clear()
        msgs = self.messages
        msgs.reverse()
        for message in msgs:
            self.inbox_widget.append(f"Message ID: {message[0]}")
            self.inbox_widget.append(f"Subject: {message[1].get('Subject')}")
            msg_content = self.get_content(message[1])
            self.inbox_widget.append(f"Content: {msg_content}")

    def fmail2gui(self, filtered_msg):
        self.inbox_widget.clear()
        for message in filtered_msg:
            self.inbox_widget.append(f"Message ID: {message[0]}")
            self.inbox_widget.append(f"Subject: {message[1].get('Subject')}")
            msg_content = self.get_content(message[1])
            self.inbox_widget.append(f"Content: {msg_content}\n")

    def filter_msgs(self):
        keyword = self.input_filter_box.text()
        similarity = 0.0
        fit_msgs = []
        model = KeyedVectors.load("model.gensim")
        for message_id, message in self.messages:
            text = self.get_content(message) + message["Subject"]
            split_text = text.lower().split()
            for word in split_text:
                try:
                    sim = model.similarity(word, keyword)
                except:
                    sim = 0
                similarity += sim
            similarity = similarity / len(split_text)
            fit_msgs.append((message_id, message, similarity))

        sorted_list = sorted(fit_msgs, key=lambda x: x[2], reverse=True)
        self.input_filter_box.clear()
        self.fmail2gui(sorted_list)
        print("FILTERING ENDED")

    def auto_resend(self, messages):
        with smtplib.SMTP_SSL(smtp_addr, smtp_port) as user:
            user.login(username, password)
            for _, message in messages:
                to_respond = email.message.EmailMessage()
                to_respond['Subject'] = message[1]['Subject']
                to_respond['From'] = username
                content = f"Message form: {message[1]['from']} \n {self.get_content(message[1])}"
                to_respond.set_content(content)
                to_respond['To'] = auto_rec_addr
                user.send_message(to_respond)

    def create_gmail_account(self):
        url = 'https://accounts.google.com/signup/v2/webcreateaccount?hl=en&flowName=GlifWebSignIn&flowEntry=SignUp'
        response = requests.get(url)
        BeautifulSoup(response.text, 'html.parser')
        form_data = {
            'firstName': 'Adam',
            'lastName': 'Ewa',
            'Username': self.create_account_username.text(),
            'Passwd': self.create_account_password.text(),
            'ConfirmPasswd': self.create_account_password.text(),
            'BirthMonth': '12',
            'BirthDay': '12',
            'BirthYear': '1999',
            'Gender': 'Other',
            'GmailTermsOfService': 'true',
            'GmailPrivacyPolicy': 'true',
            'submitbutton': 'I agree and continue',
        }
        response = requests.post(url, data=form_data)
        if response.status_code == 200:
            print(f"Account created successfully")
        else:
            print(f"An error occurred while creating the account.")
        self.create_account_username.clear()
        self.create_account_password.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = EmailClient()
    client.show()
    sys.exit(app.exec())
