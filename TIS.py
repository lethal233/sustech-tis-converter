from re import findall
import pandas as pd

import requests


class TIS:
    def __init__(self, username, password):
        self.token = requests.Session()
        self.username = username
        self.password = password
        self.route = ""
        self.jsession_id = ""
        self.header = ""

    def login(self) -> None:
        """
        copyright: @[GhostFrankWu](https://github.com/GhostFrankWu)
        :return: None
        """
        print("[\x1b[0;36m!\x1b[0m] " + "测试CAS链接...")
        try:
            # Login 服务的CAS链接有时候会变
            loginUrl = "https://cas.sustech.edu.cn/cas/login?service=https%3A%2F%2Ftis.sustech.edu.cn%2Fcas"
            req = self.token.get(loginUrl)
            assert (req.status_code == 200)
            print("[\x1b[0;32m+\x1b[0m] " + "成功连接到CAS...")
        except Exception:
            print("[\x1b[0;31mx\x1b[0m] " + "不能访问CAS, 请检查您的网络连接状态")
            exit(-1)
        print("[\x1b[0;36m!\x1b[0m] " + "登录中...")
        data = {
            'username': self.username,
            'password': self.password,
            'execution': str(req.text).split('''name="execution" value="''')[1].split('"')[0],
            '_eventId': 'submit',
        }
        req = self.token.post(loginUrl, data=data, allow_redirects=False)
        if "Location" in req.headers.keys():
            print("[\x1b[0;32m+\x1b[0m] " + "登录成功")
        else:
            print("[\x1b[0;31mx\x1b[0m] " + "用户名或密码错误，请检查")
            exit(-1)
        req = self.token.get(req.headers["Location"], allow_redirects=False)
        route = findall('route=(.+?);', req.headers["Set-Cookie"])[0]
        jsession_id = findall('JSESSIONID=(.+?);', req.headers["Set-Cookie"])[0]
        self.route = route
        self.jsession_id = jsession_id
        self.header = {
            "cookie": 'route={}; JSESSIONID={};'.format(self.route, self.jsession_id),
            "user-agent": "Mozilla/5.0",
            "Content-Type": "application/json"
        }

    def get_all_gradebook(self) -> dict:
        """
        get all the gradebook
        :return:
        """
        data = {"xn": None, "xq": None, "kcmc": None, "cxbj": "-1", "pylx": "1", "current": 1, "pageSize": 500}
        req = requests.post('https://tis.sustech.edu.cn/cjgl/grcjcx/grcjcx', json=data, headers=self.header)
        return req.json()

    def export_gradebook(self) -> None:
        """
        export the gradebook to excel
        :return:
        """
        content = self.get_all_gradebook()['content']['list']
        df = pd.DataFrame(content)
        columns = ['课程名称', '课程代码', '学年学期', '课程名称（英文）', '课程性质', '课程类别', '课程类别（英文）', '总评成绩', '院系名称', '学分', '等级成绩']
        # columns_en = ['kcmc', 'kcdm', 'xnxqmc', 'kcmc_en', 'kcxz', 'kclb', 'kclben', 'zzcj', 'yxmc', 'xf', 'xscj']
        df.drop(
            columns=['xs', 'xnxq', 'xnxqmcen', 'kcxzen', 'zzcjen', 'zzzscj', 'bkcx', 'khfs', 'cjbzmc', 'xscjen',
                     'xszscj',
                     'zpcj',
                     'zpzscj', 'sfkcx', 'sfjg', 'rwid', 'glcjid', 'sfpjcxcj', 'sfxsxq', 'pm', 'zrs', 'xnxqx', 'rwh'],
            inplace=True)
        df.columns = columns
        df.to_excel("./gradebook.xlsx", encoding="utf-8")

    def close(self) -> None:
        """
        close the session
        :return:
        """
        try:
            self.token.close()
        except Exception:
            pass
