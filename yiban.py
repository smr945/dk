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

def mail(t):
        # sender是邮件发送人邮箱，passWord是服务器授权码，mail_host是服务器地址（这里是QQsmtp服务器）
        sender = '2483193477@qq.com'  #
        passWord = 'tdzxvmrzaleeeaie'
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
if __name__ == '__main__':
    res = requests.get('http://baidu.com').status_code
    if res == 200:
        mail('success')
