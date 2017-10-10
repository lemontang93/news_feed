import os
import tornado.ioloop
import tornado.web
import tornado.locale
import tornado.escape
from tornado.options import define, options

import uimodules
from config import ITEMS_NUM_PERPAGE, TIME_LIMIT

from db_access import *

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=True, type=bool)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_id = self.get_secure_cookie("user")
        if not user_id: return None
        user = get_user(u_id=int(user_id))
        return user


class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        self.write("Hello, " + name)


class RegisterHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("register.html")
    def post(self):
        res = {"success": False, "msg": ""}
        username = self.get_argument("username")
        email = self.get_argument("email")
        password = self.get_argument("password")
        confirm_password = self.get_argument("confirm_password")

        if not username:
            res["msg"] = "用户名不能为空"
            self.finish(res)
            return

        if not email:
            res["msg"] = "邮箱不能为空"
            self.finish(res)
            return

        if not password:
            res["msg"] = "密码不能为空"
            self.finish(res)
            return

        if confirm_password != password:
            res["msg"] = "密码不一致"
            self.finish(res)
            return

        info = {
            "username": username,
            "email": email,
            "password": password
        }
        result = create_user(**info)
        if not result["success"]:
            res["msg"] = result["msg"]
            self.finish(res)
        else:
            res["success"] = True
            res["msg"] = "注册成功"
            self.write(res)


class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("login.html")
    def post(self):
        email = self.get_argument("email")
        password = self.get_argument("password")
        auth = authenticate(email=email, password=password)
        if auth["success"]:
            self.set_secure_cookie("user", str(auth["user_id"]))
        self.write(auth)


class LogoutHandler(tornado.web.RequestHandler):
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("user")
        self.redirect("/index")


class IndexHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("index.html")


class InfoHandler(BaseHandler):
    """
    获取所有个公司的feed
    """
    @tornado.web.authenticated
    def get(self):
        feeds = get_info_feed(TIME_LIMIT)
        oversea_feeds = get_oversea_info_feed(TIME_LIMIT)
        total_page = len(feeds) // ITEMS_NUM_PERPAGE + 1
        page_num = 1
        start = ITEMS_NUM_PERPAGE * (page_num - 1)
        end = ITEMS_NUM_PERPAGE * page_num
        feeds = feeds[start:end]

        self.render("information.html", feeds=feeds, oversea_feeds=oversea_feeds, total_page=total_page,
                    current_page=page_num)


class InfoFilterHandler(BaseHandler):
    """
    获取单个公司的feed
    """
    @tornado.web.authenticated
    def get(self, company_id, page_num):
        feeds = get_company_info_feed(TIME_LIMIT, company_id)
        oversea_feeds = get_oversea_info_feed(TIME_LIMIT)
        total_page = len(feeds) // ITEMS_NUM_PERPAGE + 1
        page_num = int(page_num)
        start = ITEMS_NUM_PERPAGE * (page_num - 1)
        end = ITEMS_NUM_PERPAGE * page_num
        feeds = feeds[start:end]
        self.render("information_filted.html", feeds=feeds, oversea_feeds=oversea_feeds, total_page=total_page, current_page=page_num)


class InfoCompanySearchHandler(BaseHandler):
    """
    搜索单个公司的feed
    """
    @tornado.web.authenticated
    def post(self):
        search_text = self.get_argument("search_text")
        company = search_company(search_text)[0]
        feeds = get_company_info_feed(TIME_LIMIT, company.id)
        oversea_feeds = get_oversea_info_feed(TIME_LIMIT)
        total_page = len(feeds) // ITEMS_NUM_PERPAGE + 1
        page_num = 1
        start = ITEMS_NUM_PERPAGE * (page_num - 1)
        end = ITEMS_NUM_PERPAGE * page_num
        feeds = feeds[start:end]
        self.render("information_filted.html", feeds=feeds, oversea_feeds=oversea_feeds, total_page=total_page, current_page=page_num)


class OverseaCompanySearchHandler(BaseHandler):
    """
    搜索单个公司的海外的feed
    """
    @tornado.web.authenticated
    def post(self):
        search_text = self.get_argument("search_text")
        company = search_company(search_text)[0]
        feeds = get_oversea_company_info_feed(TIME_LIMIT, company.id)
        total_page = len(feeds) // ITEMS_NUM_PERPAGE + 1
        page_num = 1
        start = ITEMS_NUM_PERPAGE * (page_num - 1)
        end = ITEMS_NUM_PERPAGE * page_num
        feeds = feeds[start:end]
        self.render("oversea_info_filted.html", feeds=feeds, total_page=total_page, current_page=page_num)



class OverseaFilterHandler(BaseHandler):
    """
    获取单个公司的海外的feed
    """
    @tornado.web.authenticated
    def get(self, company_id, page_num):
        feeds = get_oversea_company_info_feed(TIME_LIMIT, company_id)
        total_page = len(feeds) // ITEMS_NUM_PERPAGE + 1
        page_num = int(page_num)
        start = ITEMS_NUM_PERPAGE * (page_num - 1)
        end = ITEMS_NUM_PERPAGE * page_num
        feeds = feeds[start:end]
        self.render("oversea_info_filted.html", feeds=feeds, total_page=total_page, current_page=page_num)


class InfoPageHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, page_num):
        feeds = get_info_feed(TIME_LIMIT)
        oversea_feeds = get_oversea_info_feed(TIME_LIMIT)
        total_page = len(feeds) // ITEMS_NUM_PERPAGE + 1
        page_num = int(page_num)
        start = ITEMS_NUM_PERPAGE * (page_num - 1)
        end = ITEMS_NUM_PERPAGE * page_num
        feeds = feeds[start:end]
        self.render("information.html", feeds=feeds, oversea_feeds=oversea_feeds, total_page=total_page, current_page=page_num)



class OverseaInfoHandler(BaseHandler):
    """
    获取所有个公司的海外feed，显示首页
    """
    @tornado.web.authenticated
    def get(self):
        feeds = get_oversea_info_feed(60 * 72)
        total_page = len(feeds) // ITEMS_NUM_PERPAGE + 1
        page_num = 1
        start = ITEMS_NUM_PERPAGE * (page_num - 1)
        end = ITEMS_NUM_PERPAGE * page_num
        feeds = feeds[start:end]
        self.render("oversea_info.html", feeds=feeds, total_page=total_page, current_page=page_num)


class OverseaPageHandler(BaseHandler):
    """
    获取所有个公司的海外feed并分页显示
    """
    @tornado.web.authenticated
    def get(self, page_num):
        feeds = get_oversea_info_feed(60 * 72)
        total_page = len(feeds) // ITEMS_NUM_PERPAGE + 1
        page_num = int(page_num)
        start = ITEMS_NUM_PERPAGE * (page_num - 1)
        end = ITEMS_NUM_PERPAGE * page_num
        feeds = feeds[start:end]
        self.render("oversea_info.html", feeds=feeds, total_page=total_page, current_page=page_num)


class KeywordHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        keywords = get_keywords()
        self.render("keywords.html", keywords=keywords)

    @tornado.web.authenticated
    def post(self):
        res = {"success": False, "msg": ""}
        text = self.get_argument("keyword")
        result = create_keyword(text)
        if not result["success"]:
            res["msg"] = result["msg"]
            self.finish(res)
        else:
            res["success"] = True
            res["msg"] = "创建成功"
            self.write(res)


class KeywordDeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        res = {"success": False, "msg": ""}
        k_id = self.get_argument("keyword_id")
        result = delete_keyword(k_id)
        if not result:
            res["msg"] = "删除出错"
            self.finish(res)
        else:
            res["success"] = True
            res["msg"] = "删除成功"
            self.write(res)


class ReportDeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        res = {"success": False, "msg": ""}
        report_id = self.get_argument("report_id")
        result = delete_report(report_id)
        if not result:
            res["msg"] = "删除出错"
            self.finish(res)
        else:
            res["success"] = True
            res["msg"] = "删除成功"
            self.write(res)


class CleanHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        delete_feeds()
        self.redirect("/index")


class CompanyAddHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("company_add.html")


class ReportHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        reports = get_reports()
        self.render("report.html", reports=reports)


class ReportDetailHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, report_id):
        report = get_report(report_id)
        self.render("report_detail.html", report=report)


class ReportAddHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("report_add.html")

    @tornado.web.authenticated
    def post(self):
        res = {"success": False, "msg": ""}
        title = self.get_argument("title")
        author = self.get_argument("author")
        editor = self.get_argument("editor")
        lead = self.get_argument("lead")
        tags = self.get_argument("tags")
        content = self.get_argument("content")


        if not title:
            res["msg"] = "标题不能为空"
            self.finish(res)
            return

        if not author:
            res["msg"] = "作者不能为空"
            self.finish(res)
            return


        report_info = {
            "title": title,
            "author": author,
            "editor": editor,
            "lead": lead,
            "tags": tags,
            "content": content
        }

        result = create_report(**report_info)
        if not result["success"]:
            res["msg"] = result["msg"]
            self.finish(res)
        else:
            res["success"] = True
            res["msg"] = "创建成功"
            self.write(res)




class CompanyHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        companies = get_companies()
        self.render("company.html", companies=companies)

    @tornado.web.authenticated
    def post(self):
        res = {"success": False, "msg": ""}
        name_cn = self.get_argument("name_cn")
        name_en = self.get_argument("name_en")
        industry = self.get_argument("industry")

        if not name_cn:
            res["msg"] = "中文名称不能为空"
            self.finish(res)
            return

        if not name_en:
            res["msg"] = "英文名称不能为空"
            self.finish(res)
            return

        if not industry:
            res["msg"] = "所属行业不能为空"
            self.finish(res)
            return

        info = {
            "name_cn": name_cn,
            "name_en": name_en,
            "industry": industry
        }
        result = create_company(**info)
        if not result["success"]:
            res["msg"] = result["msg"]
            self.finish(res)
        else:
            res["success"] = True
            res["msg"] = "创建成功"
            res["company_id"] = result["company"].id
            self.write(res)


class CompanySearchHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        res = {"success": False, "msg": ""}
        search_text = self.get_argument("search_text")
        company_list = search_company(search_text)
        self.render("company.html", companies=company_list)




class ProfileHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, company_id):
        company = get_company(company_id)
        profile = get_profile(company_id)
        if not profile:
            create_profile(company_id)
            profile = get_profile(company_id)
        contact = get_contact(company_id)
        websites = get_company_websites(company_id)
        self.render("profile.html", company=company, profile=profile, contact=contact, websites=websites)


class ProfileEditHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, company_id):
        company = get_company(company_id)
        profile = get_profile(company_id)
        self.render("profile_edit.html", company=company, profile=profile)

    @tornado.web.authenticated
    def post(self, company_id):
        res = {"success": False, "msg": ""}
        profile_info = {
            "company_id": company_id,
            "name_cn": self.get_argument("name_cn"),
            "name_en": self.get_argument("name_en"),
            "portal": self.get_argument("portal"),
            # "contact": self.get_argument("contact"),
            "stock_code": self.get_argument("stock_code"),
        }

        response = profile_update(**profile_info)
        if not response['success']:
            res["success"] = False
            res["msg"] = "提交出错"
            self.finish(res)
        else:
            res["success"] = True
            res["msg"] = "提交成功"
            self.write(res)


class WebsiteAddHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, company_id):
        company = get_company(company_id)
        self.render("website_add.html", company=company)


class ContactAddHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, company_id):
        company = get_company(company_id)
        profile = get_profile(company_id)
        contact = get_contact(company_id)
        self.render("contact_add.html", company=company, profile=profile, contact=contact)

    @tornado.web.authenticated
    def post(self, company_id):
        res = {"success": False, "msg": ""}
        fullname = self.get_argument("fullname")
        if not fullname:
            res["msg"] = "用户名不能为空"
            self.finish(res)
            return

        contact_info = {
            "company_id": company_id,
            "name": fullname,
            "gender": self.get_argument("gender"),
            "position": self.get_argument("position"),
            "phone_number": self.get_argument("phone_number"),
            "wechat": self.get_argument("wechat"),
            "email": self.get_argument("email"),
            "comment": self.get_argument("comment"),
        }

        result = create_contact(**contact_info)
        if not result['success']:
            res["success"] = False
            res["msg"] = result["msg"]
            self.finish(res)
        else:
            res["success"] = True
            res["msg"] = "提交成功"
            self.write(res)


class ContactDeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        res = {"success": False, "msg": ""}
        contact_id = self.get_argument("contact_id")
        result = delete_contact(contact_id)
        if not result:
            res["msg"] = "删除失败"
            self.finish(res)
        else:
            res["success"] = True
            res["msg"] = "删除成功"
            self.write(res)


class WebsiteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        websites = get_websites()
        self.render("website.html", websites=websites)

    @tornado.web.authenticated
    def post(self):
        res = {"success": False, "msg": ""}
        url = self.get_argument("url")
        company_id = self.get_argument("company_id")

        if not url:
            res["msg"] = "URL不能为空"
            self.finish(res)
            return

        if (not company_id ) or (company_id == '-1'):
            res["msg"] = "请选择所属公司"
            self.finish(res)
            return

        info = {
            "url": url,
            "company_id": int(company_id),
        }
        result = create_website(**info)
        if not result["success"]:
            res["msg"] = result["msg"]
            self.finish(res)
        else:
            res["success"] = True
            res["msg"] = "创建成功"
            self.write(res)


class SubscriptionHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("subscription.html")

    @tornado.web.authenticated
    def post(self):
        res = {"success": False, "msg": ""}
        email = self.get_argument("email")
        info = {
            "username": '订阅者',
            "email": email,
            "password": 'globus#2017#subscription'
        }
        result = create_user(**info)
        if not result["success"]:
            res["msg"] = result["msg"]
            self.finish(res)
        else:
            res["success"] = True
            res["msg"] = "订阅成功"
            self.write(res)


class CompanyDeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        res = {"success": False, "msg": ""}
        company_id = self.get_argument("company_id")
        result = delete_company(company_id)
        if not result:
            res["msg"] = "删除失败"
            self.finish(res)
        else:
            res["success"] = True
            res["msg"] = "删除成功"
            self.write(res)


class WebsiteDeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        res = {"success": False, "msg": ""}
        website_id = self.get_argument("website_id")
        result = delete_website(website_id)
        if not result:
            res["msg"] = "删除失败"
            self.finish(res)
        else:
            res["success"] = True
            res["msg"] = "删除成功"
            self.write(res)


class UserManageHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        users = get_users()
        self.render("user_manage.html", users=users)


class LogHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        logs = get_logs(60)
        self.render("log.html", logs=logs)


class UserDeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        res = {"success": False, "msg": ""}
        user_id = self.get_argument("user_id")
        result = delete_user(user_id)
        if not result:
            res["msg"] = "删除失败"
            self.finish(res)
        else:
            res["success"] = True
            res["msg"] = "删除成功"
            self.write(res)




settings = {
        "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o",
        "login_url": "/login",
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "xsrf_cookies": True,
        "ui_modules": uimodules,
        "debug": options.debug,
}


application = tornado.web.Application([
    (r"/", InfoHandler),
    (r"/login", LoginHandler),
    (r"/register", RegisterHandler),
    (r"/logout", LogoutHandler),
    (r"/index", IndexHandler),
    (r"/admin", IndexHandler),
    (r"/info", InfoHandler),
    (r"/info/filter/([0-9]+)/page/([0-9]+)", InfoFilterHandler),
    (r"/info/company/search", InfoCompanySearchHandler),
    (r"/oversea/filter/([0-9]+)/page/([0-9]+)", OverseaFilterHandler),
    (r"/oversea/company/search", OverseaCompanySearchHandler),
    (r"/info/page/([0-9]+)", InfoPageHandler),
    (r"/oversea/page/([0-9]+)", OverseaPageHandler),
    (r"/oversea", OverseaInfoHandler),
    (r"/keyword", KeywordHandler),
    (r"/keyword/delete", KeywordDeleteHandler),
    (r"/report", ReportHandler),
    (r"/report/add", ReportAddHandler),
    (r"/report/delete", ReportDeleteHandler),
    (r"/report/detail/([0-9]+)", ReportDetailHandler),
    (r"/company", CompanyHandler),
    (r"/company/add", CompanyAddHandler),
    (r"/company/search", CompanySearchHandler),
    (r"/profile/([0-9]+)", ProfileHandler),
    (r"/profile/edit/([0-9]+)", ProfileEditHandler),
    (r"/contact/add/([0-9]+)", ContactAddHandler),
    (r"/contact/delete", ContactDeleteHandler),
    (r"/website/add/([0-9]+)", WebsiteAddHandler),
    (r"/website", WebsiteHandler),
    (r"/subscription", SubscriptionHandler),
    (r"/company/delete", CompanyDeleteHandler),
    (r"/website/delete", WebsiteDeleteHandler),
    (r"/user/manage", UserManageHandler),
    (r"/user/delete", UserDeleteHandler),
    (r"/log", LogHandler),
    # (r"/clean", CleanHandler),


    ], **settings)

if __name__ == '__main__':
    i18n_path = os.path.join(os.path.dirname(__file__), 'i18n/locales')
    tornado.locale.load_gettext_translations(i18n_path, 'zh_CN')
    tornado.locale.set_default_locale('zh_CN')

    application.listen(options.port)
    print("App Start running at: http://127.0.0.1:{port}".format(port=options.port))
    tornado.ioloop.IOLoop.instance().start()
