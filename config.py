# --*-- coding: utf-8 --*--


# MYSQL配置
DB = {
    'HOST': '127.0.0.1',
    'PORT': 3306,
    'DB_NAME': 'news_feed',
    'USER': '',
    'PASSWORD' : ''
}


# 发送邮件的邮箱设置

EMAIL = {
    'from_addr': '',
    'password': '',
    'smtp_server': ''
}


# 发邮件频率(小时)
SEND_MAIL_INTERVAL = 0.5


# 新闻抓取频率(分钟)
CRAWL_INTERVAL = 10

# 页面显示info时间限制(分钟)
TIME_LIMIT = 60 * 24 * 3

# md5
MD5_SALT = "some random string"


# celery
CELERY_BROKER = 'redis://localhost:6379'
CELERY_BACKEND = 'redis://localhost:6379'


# 分页
ITEMS_NUM_PERPAGE = 50