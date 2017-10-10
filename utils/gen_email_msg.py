import os
import sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.append(BASE_DIR)

from db_access import get_info_feed, get_website


def gen_message():
    message = ''
    feeds = get_info_feed(mins=30)
    if not feeds:
        return False

    w_dict = {}
    for f in feeds:
        if f.website_id not in w_dict:
            w_dict[f.website_id] = [f]
        else:
            w_dict[f.website_id].append(f)

    for w_id, info_feed in w_dict.items():
        w = get_website(w_id)
        try:
            message += '\n<h4>{company}</h4> [站点： <a href="{site}">{site}</a> ]<br>\n'.format(company=w.company.name_cn, site=w.url)
        except:
            continue
        for f in info_feed:
            message += '<a href={url}> {text} </a><br>\n'.format(url=f.url, text=f.text.strip())

    return message




if __name__ == '__main__':
    gen_message()