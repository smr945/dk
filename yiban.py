# -*- coding: utf-8 -*-
import re
import time
import traceback
import requests
import json
import random
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from util import encrypt_passwd

successnum = 0
num = 0


class YiBan:
    WFId = "5fc379fef7f94d1a09a118db05dec019"  # 疫情表单：固定表单值固定 每个大学可能不一样需要自行抓包 此处为长沙理工大学0512更新
    CSRF = "sui-bian-fang-dian-dong-xi"  # 随机值 随便填点东西
    COOKIES = {"csrf_token": CSRF}  # 固定cookie 无需更改
    HEADERS = {"Origin": "https://c.uyiban.com", "User-Agent": "yiban"}  # 固定头 无需更改

    def __init__(self, account, passwd):
        self.account = account
        self.passwd = passwd
        self.session = requests.session()

    def request(self, url, method="get", params=None, cookies=None):
        if method == "get":
            req = self.session.get(url, params=params, timeout=10, headers=self.HEADERS, cookies=cookies)
        else:
            req = self.session.post(url, data=params, timeout=10, headers=self.HEADERS, cookies=cookies)
        try:
            # print(req.json())
            return req.json()
        except:
            return None

    def login(self):
        params = {
            "account": self.account,
            "ct": 2,
            "identify": 865166025846463,
            "v": "4.7.12",
            "passwd": encrypt_passwd(self.passwd)
        }
        r = self.request(url="https://mobile.yiban.cn/api/v2/passport/login", params=params)

        if r is not None and str(r["response"]) == "100":
            self.access_token = r["data"]["access_token"]
            self.name = r["data"]["user"]["name"]
            return r
        else:
            return None

    def mail(self, t):
        # sender是邮件发送人邮箱，passWord是服务器授权码，mail_host是服务器地址（这里是QQsmtp服务器）
        sender = '2483193477@qq.com'  
        passWord = os.environ['PASSWD']
        mail_host = 'smtp.qq.com'
        # receivers是邮件接收人，用列表保存，可以添加多个
        receivers = ['2698981587@qq.com']
        # 设置email信息
        msg = MIMEMultipart()
        # 邮件主题
        msg['Subject'] = '打卡情况'
        # 发送方信息
        msg['From'] = sender
        # 邮件正文是MIMEText:
        msg_content = ''' 
        {}，没收到说明没打
        '''.format(t)
        msg.attach(MIMEText(msg_content, 'plain', 'utf-8'))
        # 登录并发送邮件
        try:
            # QQsmtp服务器的端口号为465或587
            s = smtplib.SMTP_SSL("smtp.qq.com", 465)
            s.set_debuglevel(1)
            s.login(sender, passWord)
            # 给receivers列表中的联系人逐个发送邮件
            for item in receivers:
                msg['To'] = to = item
                s.sendmail(sender, to, msg.as_string())
                print('Success!')
            s.quit()
            print("All emails have been sent over!")
        except smtplib.SMTPException as e:
            print("Falied,%s", e)
        return

    def auth(self):
        location = self.session.get("http://f.yiban.cn/iapp/index?act=iapp7463&v=%s" % self.access_token,
                                    allow_redirects=False).headers["Location"]
        verifyRequest = re.findall(r"verify_request=(.*?)&", location)[0]
        # print(verifyRequest)
        return self.request(
            "https://api.uyiban.com/base/c/auth/yiban?verifyRequest=%s&CSRF=%s" % (verifyRequest, self.CSRF),
            cookies=self.COOKIES)

    def getUncompletedList(self):
        return self.request(
            "https://api.uyiban.com/officeTask/client/index/uncompletedList?StartTime={}%2000%3A00&EndTime={}%2023%3A59&CSRF={}".format(
                t2,t2, self.CSRF),
            cookies=self.COOKIES)

    def getCompletedList(self):
        return self.request("https://api.uyiban.com/officeTask/client/index/completedList?CSRF=%s" % self.CSRF,
                            cookies=self.COOKIES)

    def getTaskDetail(self, taskId):
        return self.request(
            "https://api.uyiban.com/officeTask/client/index/detail?TaskId=%s&CSRF=%s" % (taskId, self.CSRF),
            cookies=self.COOKIES)

    def submit(self, data, extend):
        params = {
            "data": data,
            "extend": extend
        }
        return self.request(
            "https://api.uyiban.com/workFlow/c/my/apply/%s?CSRF=%s" % (self.WFId, self.CSRF), method="post",
            params=params,
            cookies=self.COOKIES)

    def getShareUrl(self, initiateId):
        return self.request(
            "https://api.uyiban.com/workFlow/c/work/share?InitiateId=%s&CSRF=%s" % (initiateId, self.CSRF),
            cookies=self.COOKIES)


if __name__ == '__main__':
    t = random.uniform(36.2, 36.6)
    t = round(t, 1)
    fmt = '%Y-%m-%d %H:%M'
    t1 = time.strftime(fmt, time.localtime(time.time()))
    t2 = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    allAccount = os.environ['USER'].split('\n')
    for i, v in enumerate(allAccount):
        allAccount[i] = v.split()
    allData = '{"c77d35b16fb22ec70a1f33c315141dbb":"%s}","2d4135d558f849e18a5dcc87b884cce5":"%s","2fca911d0600717cc5c2f57fc3702787":["湖南省","长沙市","天心区"]}' % (t, t1)

    print("++++++++++%s++++++++++" % time.strftime("%Y-%m-%d %H:%M:%S"))

    for index, account_detail in enumerate(allAccount):
        try:
            print(account_detail[0])
            yb = YiBan(account_detail[0], account_detail[1])
            if yb.login() is None:
                print("帐号或密码错误")
                continue
            result_auth = yb.auth()
            data_url = result_auth["data"].get("Data")
            if data_url is not None:  # 授权过期
                print("授权过期")
                print("访问授权网址")
                result_html = yb.session.get(url=data_url, headers=yb.HEADERS,
                                             cookies={"loginToken": yb.access_token}).text
                re_result = re.findall(r'input type="hidden" id="(.*?)" value="(.*?)"', result_html)
                print("输出待提交post data")
                print(re_result)
                post_data = {"scope": "1,2,3,"}
                for i in re_result:
                    post_data[i[0]] = i[1]
                print("进行授权确认")
                usersure_result = yb.session.post(url="https://oauth.yiban.cn/code/usersure",
                                                  data=post_data,
                                                  headers=yb.HEADERS, cookies={"loginToken": yb.access_token})
                if usersure_result.json()["code"] == "s200":
                    print("授权成功！")
                else:
                    print("授权失败！")
                    continue
                print("尝试重新二次登录")
                yb.auth()
            all_task = yb.getUncompletedList()
            if len(all_task["data"]) == 0:
                print("没有待完成的打卡任务")
            for i in all_task["data"]:
                task_detail = yb.getTaskDetail(i["TaskId"])["data"]
                if task_detail["WFId"] != yb.WFId:
                    print("表单已更新,得更新程序了")
                    exit()
                ex = {"TaskId": task_detail["Id"],
                      "title": "任务信息",
                      "content": [{"label": "任务名称", "value": task_detail["Title"]},
                                  {"label": "发布机构", "value": task_detail["PubOrgName"]},
                                  {"label": "发布人", "value": task_detail["PubPersonName"]}]}
                submit_result = yb.submit(allData, json.dumps(ex, ensure_ascii=False))
                if submit_result["code"] == 0:
                    share_url = yb.getShareUrl(submit_result["data"])["data"]["uri"]
                    print("已完成一次打卡")
                    successnum += 1
                    num += 1
                    break
                else:
                    print("打卡失败，遇到了一些错误！")
                    num += 1
            print("-------------------------------------")
            print(successnum, num)
        except:
            traceback.print_exc()
            print("遇到了一些错误~")
            num += 1
    if num == len(allAccount):
          yb.mail('成功数{},失败数{}'.format(successnum, num - successnum))
