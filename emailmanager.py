# -*- coding: UTF-8 -*-
import datetime
import logging
import os
import smtplib
from email.header import Header
from email.message import EmailMessage

from imapclient import IMAPClient


class EmailManager:

    def __init__(self, from_addr='', pwd='', host='', smtp_port=587, imap_port=7993, template=None):
        self._from_addr = from_addr
        self._login = ''
        self._password = pwd
        self._host = host
        self._smtp_port = smtp_port
        self._imap_port = imap_port

        self._server_smtp = None
        self._server_imap = None

        self._logger = None
        self._template = template

        self.setupLogger()

    def setupLogger(self):
        now = datetime.datetime.now()
        filename = f'./logs/log-{now.date()}.txt'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
        fh = logging.FileHandler(filename=filename, encoding='UTF-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(formatter)
        self._logger = logging.getLogger('main')
        self._logger.addHandler(fh)
        self._logger.addHandler(sh)
        self._logger.setLevel(logging.DEBUG)

    def setCredentials(self, *creds):
        self._from_addr, self._login, self._password, self._host, self._smtp_port, self._imap_port = creds

    def send(self, emailData: dict, addrs: dict):
        emails = self._build_emails(emailData, addrs, self._from_addr)
        ok = self._connect()
        if not ok:
            return False

        ok = self._send_emails(emails=emails)
        if not ok:
            return False

        self._disconnect()

        return True

    def _connect(self):
        if not self._from_addr or not self._password or not self._host or not self._smtp_port or not self._imap_port:
            self._logger.error('No credentials provided')
            return False
        try:
            # login to IMAP to store messages
            self._logger.info(f'connect to IMAP: {self._host}:{self._imap_port}')
            self._server_imap = IMAPClient(host=self._host, port=self._imap_port, use_uid=True)
            self._server_imap.login(self._login, self._password)

            # login to SMTP to send messages
            self._logger.info(f'connect to SMPT: {self._host}:{self._smtp_port}')
            self._server_smtp = smtplib.SMTP('mail.pulsarnpp.ru', 587)
            self._server_smtp.login(self._login, self._password)

        except Exception as ex:   # FIXME narrow except clause
            self._logger.error(f'server connect error: {ex}')
            return False
        return True

    def _disconnect(self):
        self._logger.info('disconnect')
        try:
            self._server_imap.logout()
            self._server_smtp.quit()
        except Exception as ex:
            self._logger.error(f'disconnect error {ex}')

    def _send_emails(self, emails):
        self._logger.info('send messages')
        try:
            for msg in emails:
                self._logger.info(f'send {msg.values()}')
                self._server_smtp.send_message(msg)
                self._server_imap.append('Sent', msg.as_string())
        except Exception as ex:
            self._logger.error(f'email send error: {ex}')
            return False

        self._logger.info('send success')
        return True

    def _build_emails(self, batches: dict, addrs: dict, from_addr: str):
        self._logger.info('build emails')
        result = list()
        for batch, devs in batches.items():
            for index, (dev, specs) in enumerate(devs.items()):
                msg = EmailMessage()
                h = Header(s=self._template.subject.replace('__LAUNCH__', batch), charset='utf-8')
                msg['From'] = from_addr
                send_to = addrs.get(dev)
                if not send_to:
                    self._logger.error(f'missing email address for {dev}')
                    continue
                fullname, msg['To'] = send_to
                msg['Subject'] = h.encode(linesep='')
                msg.set_content(self._template.message.replace('__NAME__', fullname).replace('__CHIP_LIST__', '\n'.join(
                    [f'{index + 1}. {spec.name}' for index, spec in enumerate(specs)]
                )))
                result.append(msg)
        return result


