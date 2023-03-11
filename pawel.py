import sys
import os

from PySide6.QtCore import *
from PySide6.QtWidgets import *

from wno2mailUI import Ui_MainWindow

import smtplib
import imaplib

import email
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

from gensim.models import KeyedVectors
import re
import pickle


class Message:
    def __init__(self, m_number, m_from, m_to, m_BCC, m_date, m_subject, m_content):
        self.m_number = m_number
        self.m_from = m_from
        self.m_to = m_to
        self.m_BCC = m_BCC
        self.m_date = m_date
        self.m_subject = m_subject
        self.m_content = m_content
        self.similarity = 0.0

    def getContent(self):
        return self.m_content

    def getSim(self):
        return self.similarity

    def getSub(self):
        return self.m_subject

    def getFrom(self):
        return self.m_from

    def getDate(self):
        return self.m_date

    def getNum(self):
        return self.m_number

    def checkSimilarity(self, model, keyword):
        self.similarity = 0.0
        text = self.m_subject + " " + self.m_content
        text = re.sub(r'[^A-Za-z0-9 \n]+', '', text)
        split_text = text.lower().split()
        for word in split_text:
            try:
                sim = model.similarity(word, keyword)
            except:
                sim = 0
            if sim > 0.5:
                self.similarity = self.similarity + sim
        if len(split_text) > 0:
            self.similarity = self.similarity / len(split_text)
        else:
            self.similarity = 0


class Mail(QMainWindow):
    def __init__(self):
        super(Mail, self).__init__()
        self.ar_list = []
        self.mail_list = []
        self.saved_messages = []
        self.L_model = KeyedVectors.load("word-vectors.gensim")
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(10000)

        self.ui.loginButton.clicked.connect(self.login)
        self.ui.sendButton.clicked.connect(self.send)
        self.ui.addtoARButton.clicked.connect(self.add2ar)
        self.ui.attachButton.clicked.connect(self.attach)
        self.ui.comboBox.activated.connect(self.mailboxChange)
        self.ui.refreshButton.clicked.connect(self.refresh)
        self.ui.emailList.activated.connect(self.displayEmail)
        self.ui.searchButton.clicked.connect(self.search)
        self.refresh_timer.timeout.connect(self.update)
        self.ui.keywordEdit.returnPressed.connect(self.search)

    def update(self) -> None:
        if self.ui.autoRefreshCheckBox.isChecked():
            if self.ui.keywordEdit.text():
                self.search()
            else:
                self.refresh()

    def login(self):
        try:
            self.server = smtplib.SMTP(self.ui.serverEdit.text(), self.ui.portEdit.text())
            self.server.ehlo()
            self.server.starttls()
            self.server.ehlo()
            self.server.login(self.ui.emailEdit.text(), self.ui.passwordEdit.text())
            self.IMAPserver = imaplib.IMAP4_SSL(self.ui.IMAPserverEdit.text(), self.ui.IMAPportEdit.text())
            self.IMAPserver.login(self.ui.emailEdit.text(), self.ui.passwordEdit.text())
            self.IMAPserver.select("Inbox")

            self.ui.serverEdit.setEnabled(False)
            self.ui.portEdit.setEnabled(False)
            self.ui.passwordEdit.setEnabled(False)
            self.ui.emailEdit.setEnabled(False)
            self.ui.loginButton.setEnabled(False)
            self.ui.IMAPportEdit.setEnabled(False)
            self.ui.IMAPserverEdit.setEnabled(False)

            self.ui.emailList.setEnabled(True)
            self.ui.toEdit.setEnabled(True)
            self.ui.subjectEdit.setEnabled(True)
            self.ui.sendButton.setEnabled(True)
            self.ui.attachButton.setEnabled(True)
            self.ui.AREmailEdit.setEnabled(True)
            self.ui.ARtextEdit.setEnabled(True)
            self.ui.addtoARButton.setEnabled(True)
            self.ui.emailBrowser.setEnabled(True)
            self.ui.keywordEdit.setEnabled(True)
            self.ui.searchButton.setEnabled(True)
            self.ui.comboBox.setEnabled(True)
            self.ui.refreshButton.setEnabled(True)
            self.ui.contentEdit.setEnabled(True)
            self.ui.ARlistView.setEnabled(True)

            self.refresh_timer.start()

            self.msg = MIMEMultipart()
        except smtplib.SMTPAuthenticationError:
            message_box = QMessageBox()
            message_box.setText("Authentication error!")
            message_box.exec()
        except:
            message_box = QMessageBox()
            message_box.setText("Something went wrong!")
            message_box.exec()
        pass

    def send(self):
        try:
            self.msg['From'] = self.ui.emailEdit.text()
            self.msg['To'] = self.ui.toEdit.text()
            self.msg['Subject'] = self.ui.subjectEdit.text()
            self.msg.attach(MIMEText(self.ui.contentEdit.toPlainText(), 'plain'))

            text = self.msg.as_string()
            self.server.sendmail(self.ui.emailEdit.text(), self.ui.toEdit.text(), text)

            message_box = QMessageBox()
            message_box.setText("Mail sent!")
            message_box.exec()

            self.ui.toEdit.clear()
            self.ui.subjectEdit.clear()
            self.ui.contentEdit.clear()
            self.ui.label_11.setText("Attachments:")
            self.msg = MIMEMultipart()

        except:
            pass

    def autoSend(self, to):
        try:
            self.automsg = MIMEMultipart()
            self.automsg['From'] = self.ui.emailEdit.text()
            self.automsg['To'] = to
            self.automsg['Subject'] = "Automated Response"
            self.automsg.attach(MIMEText(self.ui.ARtextEdit.toPlainText(), 'plain'))
            text = self.automsg.as_string()
            self.server.sendmail(self.ui.emailEdit.text(), to, text)

        except:
            pass

    def attach(self):
        options = QFileDialog.Options()
        filenames, _ = QFileDialog.getOpenFileNames(self, "Open File", "", "All Files (*.*)", options=options)
        if filenames:
            for filename in filenames:
                attachment = open(filename, 'rb')

                filename = filename[filename.rfind("/") + 1:]
                p = MIMEBase('application', 'octet-stream')
                p.set_payload(attachment.read())
                encoders.encode_base64(p)
                p.add_header("Content-Disposition", f"attachment; filename={filename}")
                self.msg.attach(p)
                if not self.ui.label_11.text().endswith(":"):
                    self.ui.label_11.setText(self.ui.label_11.text() + ",")
                self.ui.label_11.setText(self.ui.label_11.text() + " " + filename)

    def mailboxChange(self, index):
        match index:
            case 0:
                self.IMAPserver.select("Inbox")
            case 1:
                self.IMAPserver.select("Sent")
        self.refresh()

    def refresh(self):
        self.ui.emailList.clear()
        self.saved_messages.clear()
        _, msg_numbers = self.IMAPserver.search(None, "ALL")
        list_entries = []
        for msg_number in msg_numbers[0].split():
            _, data = self.IMAPserver.fetch(msg_number, "(RFC822)")
            message = email.message_from_bytes(data[0][1])
            if self.ui.comboBox.currentIndex() == 0:
                short = message.get('From') + " | " + message.get('Subject')
            else:
                short = message.get('To') + " | " + message.get('Subject')
            list_entries.append(short)
            content = ""
            for part in message.walk():
                try:
                    content = part.get_payload(decode=True).decode()
                except:
                    pass

            self.saved_messages.append(Message(msg_number,
                                               message.get('From'),
                                               message.get('To'),
                                               message.get('BCC'),
                                               message.get('Date'),
                                               message.get('Subject'),
                                               content))

        self.ui.emailList.addItems(list_entries)
        if self.ui.comboBox.currentIndex() == 0:
            try:
                f = open("email_history.bin", "rb")
                retrieved_messages = pickle.load(f)
                ret_msg = []
                cur_msg = []
                for retrieved in retrieved_messages:
                    ret_msg.append((retrieved.getDate(), retrieved.getFrom()))

                for current in self.saved_messages:
                    cur_msg.append((current.getDate(), current.getFrom()))
                if len(cur_msg) > len(ret_msg):
                    difference = set(cur_msg) ^ set(ret_msg)
                    if difference:
                        model = self.ui.ARlistView.model()
                        for diff in difference:
                            for row in range(model.rowCount()):
                                index = model.index(row, 0)
                                address = model.data(index, Qt.DisplayRole)
                                if address in diff[1]:
                                    self.autoSend(address)
                f.close()
            except FileNotFoundError:
                message_box = QMessageBox()
                message_box.setText("A file was missing")
                message_box.exec()
            except:
                message_box = QMessageBox()
                message_box.setText("Something went wrong!")
                message_box.exec()

            f = open("email_history.bin", "wb")
            pickle.dump(self.saved_messages, f)
            f.close()

    def displayEmail(self):
        self.ui.emailBrowser.setText(self.saved_messages[self.ui.emailList.currentRow()].getContent())

    def search(self):
        self.refresh()
        for message in self.saved_messages:
            message.checkSimilarity(self.L_model, self.ui.keywordEdit.text())
        self.saved_messages.sort(key=lambda x: x.getSim(), reverse=True)
        self.ui.emailList.clear()
        list_entries = []
        for message in self.saved_messages:
            if self.ui.comboBox.currentIndex() == 0:
                entry = message.getFrom() + ' | ' + message.getSub()
            else:
                entry = message.getTo() + ' | ' + message.getSub()
            list_entries.append(entry)
        self.ui.emailList.addItems(list_entries)

    def add2ar(self):
        self.ui.ARlistView.addItem(self.ui.AREmailEdit.text())
        self.ui.AREmailEdit.clear()


if __name__ == "__main__":
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    app = QApplication(sys.argv)

    window = Mail()
    window.show()

    sys.exit(app.exec())
