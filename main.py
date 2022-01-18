# -*- coding:utf-8 -*-
from TIS import TIS


def get_username_password():
    username = input("请输入你的学号please input your SID: ")
    password = input("请输入你的密码please input your password: ")
    return username, password


def main():
    sid, pwd = get_username_password()
    tis_session = TIS(sid, pwd)
    try:
        tis_session.login()
        tis_session.export_gradebook()
    except Exception as e:
        print(e)
    finally:
        tis_session.close()


if __name__ == '__main__':
    main()
