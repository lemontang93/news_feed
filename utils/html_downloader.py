# coding=utf-8

import requests

import os
import sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.append(BASE_DIR)
from utils.log import log, ERROR


def save_html(content):
    with open('2.html', 'w', encoding='utf-8') as f:
        f.write(content)


def crawl(url):
    s = requests.session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
    }
    response = s.get(url, headers=headers, timeout=30)
    if response.status_code == 200:
        text = response.text
        encoding = response.encoding
        apparent_encoding = response.apparent_encoding

        if encoding not in ['utf-8', 'UTF-8']:
            try:
                if apparent_encoding in ['utf-8', 'UTF-8', 'UTF-8-SIG']:
                    text = response.text.encode(encoding).decode('utf8')
                else:
                    if encoding == 'gb2312' and apparent_encoding == 'GB2312':
                        text = response.text.encode('utf8').decode('utf8')
                    elif encoding == 'ISO-8859-1' and apparent_encoding == 'ISO-8859-1':
                        text = response.text.encode('utf8').decode('utf8')
                    elif encoding == 'ISO-8859-1' and apparent_encoding == 'Big5':
                        text = response.text.encode(encoding).decode('big5').encode('utf8').decode('utf8')
                    elif encoding == 'big5' and apparent_encoding == 'Big5':
                        text = response.text.encode(encoding).decode('big5').encode('utf8').decode('utf8')
                    else:
                        text = response.text.encode(encoding).decode('gbk').encode('utf8').decode('utf8')

            except:
                # log(ERROR, '编码错误 [{encoding}] [{url}]'.format(encoding=encoding, url=url))
                return False
        # save_html(text)
        return text
    return False





if __name__ == '__main__':
    # crawl('http://www.xxcig.com/xwzx/index.htm')
    # crawl('http://www.hnair.com/guanyuhaihang/hhxw/hhxw/')
    # crawl('http://static.lenovo.com/ww/lenovo/investor_relations.html')
    # crawl('http://www.fhkg.com/webpage/ch/cms/investor/index.shtml')
    # crawl('http://www.ausnutria.com.hk/en/ir/news.php')
    # crawl("http://www.ccland.com.hk/big5/media/press.php")
    crawl("http://www.magang.com.hk/eng/announcement.asp")

