# --*-- coding: utf-8 --*--
import time

from utils.gen_email_msg import gen_message

__author__ = 'nolan'

import os
import sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.append(BASE_DIR)

from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
from config import EMAIL
from db_access import get_users
from utils.blacklist import blacklist_email


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def send_mail(to_addr):
    from_addr = EMAIL['from_addr']
    password = EMAIL['password']
    smtp_server = EMAIL['smtp_server']

    message = gen_message()
    # message = 'test'
    if not message:
        return
    msg = MIMEText(message, 'html', 'utf-8')



    # server = smtplib.SMTP(smtp_server, 25)
    server = smtplib.SMTP_SSL(smtp_server, 465)
    server.set_debuglevel(1)
    server.login(from_addr, password)

    msg['From'] = _format_addr(u'GLOBUS Bot<%s>' % from_addr)
    msg['To'] = _format_addr(u'订阅者 <%s>' % to_addr)
    msg['Subject'] = Header(u'网站监控最新动态', 'utf-8').encode()
    server.sendmail(from_addr, [to_addr], msg.as_string())
    # time.sleep(10)

    server.quit()


if __name__ == "__main__":
    user_list = get_users()
    addr_list = []
    for u in user_list:
        if u.email not in blacklist_email:
            addr_list.append(u.email)

    for to in addr_list:
        try:
            send_mail(to)
        except Exception as e:
            print(str(e))