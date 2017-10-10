# --*-- coding: utf-8 --*--

import datetime
import hashlib
from sqlalchemy import desc
from config import MD5_SALT
from models import *
from utils.blacklist import blacklist_title_text

session = DBSession()

import os
import sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.append(BASE_DIR)

def hash_password(text):
    text_encoded = (text+MD5_SALT).encode('utf-8')
    md5_code = hashlib.md5(text_encoded).hexdigest()
    return md5_code


def create_user(**kwargs):
    try:
        res = {"success": False, "msg": ""}
        user = session.query(User).filter_by(email=kwargs["email"]).first()
        if user:
            res["msg"] = "已存在"
            return res

        session.add(User(username=kwargs["username"], email=kwargs["email"], password=hash_password(kwargs["password"])))
        # session.commit()
        session.flush()
        # user = session.query(User).filter_by(username=kwargs["username"]).first()
        res["success"] = True
        return res
    except Exception as e:
        # print(str(e))
        # session.rollback()
        res["msg"] = "创建出错"
        return res


def authenticate(email=None, password=None):
    res = {"success": False, "msg": "", "user_id": None}
    user = session.query(User).filter_by(email=email).first()
    if not user:
        res["msg"] = "用户名不存在"
        return res
    if user.password != hash_password(password):
        res["msg"] = "用户名与密码不符"
        return res
    res["success"] = True
    res["user_id"] = user.id
    res["msg"] = "认证成功"
    return res


def get_user(u_id=None):
    user = session.query(User).filter_by(id=u_id).first()
    return user


def get_companies():
    companies = session.query(Company).all()
    # companies = session.query(Company).order_by(desc(Company.create_at)).all()
    return companies


def get_company(c_id=None):
    company = session.query(Company).filter_by(id=c_id).first()
    return company


def search_company(text):
    company_list = session.query(Company).filter(Company.name_cn.contains(text)).all()
    return company_list


def get_profile(c_id=None):
    profile = session.query(CompanyProfle).filter_by(company_id=c_id).first()
    return profile


def get_contact(c_id=None):
    contact = session.query(ContactPerson).filter_by(company_id=c_id).all()
    return contact


def get_websites():
    websites = session.query(Website).all()
    return websites


def get_websites_desc():
    websites = session.query(Website).order_by(desc(Website.create_at)).all()
    return websites


def get_website(w_id):
    website = session.query(Website).filter_by(id=w_id).first()
    return website


def get_company_websites(c_id):
    websites = session.query(Website).filter_by(company_id=c_id).all()
    return websites


def get_users():
    users = session.query(User).all()
    return users


def get_logs(mins):
    since = datetime.datetime.now() - datetime.timedelta(minutes=mins)
    logs = session.query(CrawlerLOG).filter(CrawlerLOG.create_at > since).order_by(desc(CrawlerLOG.create_at)).all()

    flag = datetime.datetime.now() - datetime.timedelta(days=1)
    old_logs = session.query(CrawlerLOG).filter(CrawlerLOG.create_at <= flag).all()
    for log_item in old_logs:
        session.delete(log_item)
    session.flush()
    return logs


def delete_company(company_id):
    try:
        websites = session.query(Website).filter_by(company_id=company_id).all()
        for w in websites:
            session.delete(w)
            # session.commit()
        company = session.query(Company).filter_by(id=company_id).first()
        session.delete(company)
        session.flush()
        # session.commit()
        return True
    except Exception as e:
        # print(str(e))
        # session.rollback()
        return False


def delete_website(website_id):
    try:
        website = session.query(Website).filter_by(id=website_id).first()
        session.delete(website)
        # session.commit()
        session.flush()
        return True
    except Exception as e:
        # print(str(e))
        # session.rollback()
        return False


def delete_user(user_id):
    try:
        user = session.query(User).filter_by(id=user_id).first()
        session.delete(user)
        # session.commit()
        session.flush()
        return True
    except Exception as e:
        # print(str(e))
        # session.rollback()
        return False


def save_html_content(w_id, content):
    try:
        html = session.query(HtmlContent).filter_by(website_id=w_id).first()
        if html:
            html.content = content
            html.update_at = datetime.datetime.now()
            # session.commit()
            session.flush()
        else:
            session.add(HtmlContent(website_id=w_id, content=content))
            # session.commit()
            session.flush()
        return True
    except Exception as e:
        # print(str(e))
        session.rollback()
        return False


def save_info_feed(url, text, w_id, c_id):
    try:
        feed = session.query(InfoFeed).filter_by(text=text).first()
        if feed:
            return False
        session.add(InfoFeed(url=url, text=text, website_id=w_id, company_id=c_id))
        # session.commit()
        session.flush()
        return True
    except Exception as e:
        # print(str(e))
        session.rollback()
        return False


def get_info_feed(mins):
    try:
        since = datetime.datetime.now() - datetime.timedelta(minutes=mins)
        new_info_feed = session.query(InfoFeed).filter(InfoFeed.create_at > since).order_by(desc(InfoFeed.create_at)).all()
        flag = datetime.datetime.now() - datetime.timedelta(days=3)
        old_info_feed = session.query(InfoFeed).filter(InfoFeed.create_at <= flag).all()
        for f in old_info_feed:
            session.delete(f)
            # session.commit()
        session.flush()
        return new_info_feed
    except Exception as e:
        # print(str(e))
        # session.rollback()
        return False


def get_company_info_feed(mins, company_id):
    try:
        since = datetime.datetime.now() - datetime.timedelta(minutes=mins)
        new_info_feed = session.query(InfoFeed).filter(InfoFeed.create_at > since).filter_by(company_id=company_id).order_by(desc(InfoFeed.create_at)).all()
        flag = datetime.datetime.now() - datetime.timedelta(days=3)
        old_info_feed = session.query(InfoFeed).filter(InfoFeed.create_at <= flag).all()
        for f in old_info_feed:
            session.delete(f)
            # session.commit()
        session.flush()
        return new_info_feed
    except Exception as e:
        # print(str(e))
        # session.rollback()
        return False


def get_oversea_info_feed(mins):
    try:
        since = datetime.datetime.now() - datetime.timedelta(minutes=mins)
        # new_info_feed = session.query(InfoFeed).filter(InfoFeed.create_at > since).\
        #     filter(InfoFeed.text.contains(['世界', '国际', '海外', '出海', '中国'])).\
        #     order_by(desc(InfoFeed.create_at)).all()

        keyword_list = []
        keyword_objects = session.query(Keyword).all()
        for k in keyword_objects:
            keyword_list.append(k.text)

        new_info_feed = session.query(InfoFeed).filter(InfoFeed.create_at > since).order_by(desc(InfoFeed.create_at))

        result = []
        for keyword in keyword_list:
            result.extend(new_info_feed.filter(InfoFeed.text.contains(keyword)).all())

        for feed in result:
            for t in blacklist_title_text:
                if feed.text.find(t) != -1:
                    result.remove(feed)

        result = sorted(result, key=lambda c : c.create_at, reverse=True)
        session.flush()
        return result


    except Exception as e:
        # print(str(e))
        # session.rollback()
        return False


def get_oversea_company_info_feed(mins, company_id):
    try:
        since = datetime.datetime.now() - datetime.timedelta(minutes=mins)
        # new_info_feed = session.query(InfoFeed).filter(InfoFeed.create_at > since).\
        #     filter(InfoFeed.text.contains(['世界', '国际', '海外', '出海', '中国'])).\
        #     order_by(desc(InfoFeed.create_at)).all()

        keyword_list = []
        keyword_objects = session.query(Keyword).all()
        for k in keyword_objects:
            keyword_list.append(k.text)

        new_info_feed = session.query(InfoFeed).filter(InfoFeed.create_at > since).filter_by(company_id=company_id).\
            order_by(desc(InfoFeed.create_at))

        result = []
        for keyword in keyword_list:
            result.extend(new_info_feed.filter(InfoFeed.text.contains(keyword)).all())

        for feed in result:
            for t in blacklist_title_text:
                if feed.text.find(t) != -1:
                    result.remove(feed)

        result = sorted(result, key=lambda c : c.create_at, reverse=True)
        session.flush()
        return result


    except Exception as e:
        # print(str(e))
        # session.rollback()
        return False


def get_keywords():
    keywords = session.query(Keyword).order_by(desc(Keyword.create_at)).all()
    return keywords


def delete_feeds():
    try:
        old_info_feed = session.query(InfoFeed).all()
        for f in old_info_feed:
            session.delete(f)
            # session.commit()
        session.flush()
        return True
    except Exception as e:
        # print(str(e))
        # session.rollback()
        return False



def create_company(**kwargs):
    try:
        res = {"success": False, "msg": "", 'company': None}
        company = session.query(Company).filter_by(name_cn=kwargs["name_cn"]).first()
        if company:
            res["msg"] = "公司已存在"
            return res
        session.add(Company(name_cn=kwargs["name_cn"], name_en=kwargs["name_en"], industry=kwargs["industry"]))
        # session.commit()
        session.flush()
        company = session.query(Company).filter_by(name_cn=kwargs["name_cn"]).first()
        res["success"] = True
        res["company"] = company
        return res
    except Exception as e:
        # print(str(e))
        # session.rollback()
        res["msg"] = "创建出错"
        return res


def create_website(**kwargs):
    try:
        res = {"success": False, "msg": ""}
        website = session.query(Website).filter_by(url=kwargs["url"]).first()
        if website:
            res["msg"] = "站点已存在"
            return res
        session.add(Website(url=kwargs["url"], company_id=kwargs["company_id"]))
        # session.commit()
        session.flush()
        res["success"] = True
        return res
    except Exception as e:
        # print(str(e))
        # session.rollback()
        res["msg"] = "创建出错"
        return res


def create_profile(c_id):
    try:
        res = {"success": False, "msg": ""}
        website = session.query(Website).filter_by(company_id=c_id).first()
        session.add(CompanyProfle(company_id=c_id, portal=website.url))
        # session.commit()
        session.flush()
        res["success"] = True
        return res
    except Exception as e:
        # print(str(e))
        # session.rollback()
        res["msg"] = "创建出错"
        return res


def profile_update(**kwargs):
    try:
        res = {"success": False, "msg": ""}
        company = session.query(Company).filter_by(id=kwargs["company_id"]).first()
        profile = session.query(CompanyProfle).filter_by(company_id=kwargs["company_id"]).first()
        if kwargs["name_cn"] != company.name_cn:
            company.name_cn = kwargs["name_cn"]

        if kwargs["name_en"] != company.name_en:
            company.name_en = kwargs["name_en"]

        if kwargs["portal"] != profile.portal:
            profile.portal = kwargs["portal"]

        # if kwargs["contact"] != profile.contact:
        #     profile.contact = kwargs["contact"]

        if kwargs["stock_code"] != profile.stock_code:
            profile.stock_code = kwargs["stock_code"]

        # session.commit()
        session.flush()
        res["success"] = True
        return res
    except Exception as e:
        # print(str(e))
        # session.rollback()
        res["msg"] = "更新出错"
        return res


def create_keyword(text):
    try:
        res = {"success": False, "msg": ""}
        keyword = session.query(Keyword).filter_by(text=text).first()
        if keyword:
            res["msg"] = "已存在"
            return res

        session.add(Keyword(text=text))
        # session.commit()
        session.flush()
        res["success"] = True
        return res
    except Exception as e:
        # print(str(e))
        # session.rollback()
        res["msg"] = "创建出错"
        return res


def delete_keyword(k_id):
    try:
        keyword = session.query(Keyword).filter_by(id=k_id).first()
        session.delete(keyword)
        # session.commit()
        session.flush()
        return True
    except Exception as e:
        # print(str(e))
        # session.rollback()
        return False


def delete_report(report_id):
    try:
        report = session.query(Report).filter_by(id=report_id).first()
        session.delete(report)
        # session.commit()
        session.flush()
        return True
    except Exception as e:
        # print(str(e))
        # session.rollback()
        return False


def create_contact(**kwargs):
    try:
        res = {"success": False, "msg": ""}
        session.add(ContactPerson(company_id=kwargs["company_id"], name=kwargs["name"],
                                  gender=kwargs["gender"], position=kwargs["position"],
                                  phone_number=kwargs["phone_number"], wechat=kwargs["wechat"],
                                  email=kwargs["email"], comment=kwargs["comment"]))
        # session.commit()
        session.flush()
        res["success"] = True
        return res
    except Exception as e:
        # print(str(e))
        # session.rollback()
        res["msg"] = "创建出错"
        return res


def create_report(**kwargs):
    try:
        res = {"success": False, "msg": ""}
        session.add(Report(title=kwargs["title"], author=kwargs["author"], editor=kwargs["editor"],
                           lead=kwargs["lead"], tags=kwargs["tags"], content=kwargs["content"]))
        # session.commit()
        session.flush()
        res["success"] = True
        return res
    except Exception as e:
        # print(str(e))
        # session.rollback()
        res["msg"] = "创建出错"
        return res


def delete_contact(contact_id):
    try:
        contact = session.query(ContactPerson).filter_by(id=contact_id).first()
        session.delete(contact)
        # session.commit()
        session.flush()
        return True
    except Exception as e:
        # print(str(e))
        # session.rollback()
        return False


def get_reports():
    reports = session.query(Report).order_by(desc(Report.create_at)).all()
    return reports


def get_report(report_id):
    report = session.query(Report).filter_by(id=report_id).first()
    return report


def log2db(level, msg):
    try:
        session.add(CrawlerLOG(level=level, text=msg))
        session.flush()
    except:
        pass