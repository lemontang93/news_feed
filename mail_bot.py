# --*-- coding: utf-8 --*--

import os
import sys


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

import time
from utils.send_email import send_mail
from config import SEND_MAIL_INTERVAL
from db_access import get_users
from utils.blacklist import blacklist_email



def mail_bot():
    while True:
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

        time.sleep(60 * 60 * SEND_MAIL_INTERVAL)






if __name__ == '__main__':
    mail_bot()