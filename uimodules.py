import tornado.web
import datetime

class TZ(tornado.web.UIModule):
    def render(self, utc, show_comments=False):
        cst_time = utc + datetime.timedelta(hours=8)
        return cst_time


class HTML_PARSE(tornado.web.UIModule):
    def render(self, content, show_comments=False):
        new_content = content.replace("\n", "<br>")
        return new_content