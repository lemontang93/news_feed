# coding=utf-8

import os
import sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.append(BASE_DIR)

import datetime
from db_access import log2db

NOTICE, RECORD, WARNING, ERROR, FATALITY, PUSH = 0, 1, 2, 4, 8, 16


def log(level, output, func_name=''):
    t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if level == NOTICE:
        msg = '[NOTICE] %s %s' % (t, output)
        print(msg)
        log2db(level, msg)
    elif level == RECORD:
        msg = '[RECORD] %s %s' % (t, output)
        print(msg)
        log2db(level, msg)
    elif level == WARNING:
        msg = '[WARNING] %s %s %s' % (t, func_name, output)
        print(msg)
        log2db(level, msg)
    elif level == ERROR:
        msg = '[ERROR] %s %s %s' % (t, func_name, output)
        print(msg)
        log2db(level, msg)
    elif level == FATALITY:
        msg = '[FATALITY] %s %s' % (t, output)
        print(msg)
        log2db(level, msg)

