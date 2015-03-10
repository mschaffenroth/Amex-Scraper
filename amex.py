import sys
import os
import helper as hlp
import requests
import time
from dateutil import parser
from pytz import timezone
from datetime import datetime, timedelta
import urllib
import subprocess
from StringIO import *
from bs4 import BeautifulSoup
import re
import pandas as pd
from unidecode import unidecode

class Amex:
    
    def __init__(self, user_name=None, password=None):
        self.s = requests.session()
        self.s.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.43 Safari/537.31'
        self.s.headers['Accept-Encoding'] = "gzip,deflate,sdch"
        self.s.headers['Accept'] = 'application/json, text/javascript, */*'
        self.s.headers['Accept-Language'] = 'en-US,en;q=0.8'
        self.s.headers['X-Requested-With'] = 'XMLHttpRequest'
        self.logged_in = False
        self.account_data = None
        self.user_name = user_name
        self.password = password
        if user_name is not None and password is not None:
            self.response_html = self.login()
            
    def login(self, user_name=None, password=None, ques_dict=None):
        if user_name is not None:
            self.user_name = user_name
        if password is not None:
            self.password = password
        ## Login Script
        # Hit login Page
        home_page = 'https://online.americanexpress.com/myca/logon/us/action/LogonHandler?request_type=LogonHandler&Face=en_US'
        res = self.s.get(home_page)
        now = datetime.now()
        login_page = 'https://online.americanexpress.com/myca/logon/us/action/LogLogonHandler?request_type=LogLogonHandler&location=us_logon1'
        data = {
        'Face' :'en_US',
        'Logon' : 'Logon',
        'ReqSource' : '',
        'checkboxValueID' : 'checked',
        'devicePrint' :'version%3D1%26pm%5Ffpua%3Dmozilla%2F5%2E0%20%28macintosh%3B%20intel%20mac%20os%20x%2010%5F9%5F0%29%20applewebkit%2F537%2E36%20%28khtml%2C%20like%20gecko%29%20chrome%2F36%2E0%2E1985%2E125%20safari%2F537%2E36%7C5%2E0%20%28Macintosh%3B%20Intel%20Mac%20OS%20X%2010%5F9%5F0%29%20AppleWebKit%2F537%2E36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F36%2E0%2E1985%2E125%20Safari%2F537%2E36%7CMacIntel%26pm%5Ffpsc%3D24%7C1280%7C800%7C774%26pm%5Ffpsw%3D%26pm%5Ffptz%3D%2D4%26pm%5Ffpln%3Dlang%3Den%2DUS%7Csyslang%3D%7Cuserlang%3D%26pm%5Ffpjv%3D1%26pm%5Ffpco%3D1',
        'acctSelected' : 'Cards+%96+My+Account',
        'acctSelectedURL': '/myca/logon/us/action/LogLogonHandler?request_type=LogLogonHandler&location=us_logon1',
        'TARGET' : 'https://online.americanexpress.com/myca/acctmgmt/us/myaccountsummary.do?request_type=authreg_acctAccountSummary&Face=en_US&omnlogin=us_enterpriselogin_myca',
        'DestPage' : 'https://online.americanexpress.com/myca/acctmgmt/us/myaccountsummary.do?request_type=authreg_acctAccountSummary&Face=en_US&omnlogin=us_enterpriselogin_myca',
        'act' : 'soa',
        'brandname' : '',
        'USERID' : '',
        'PWD' : '',
        'errMsgValueInPage': 'false',
        'errMsgValue' : '',
        'isDestFound' : '',
        'pageState' : 'logOff',
        'b_hour' : str(int(now.strftime('%H'))-4),
        'b_minute' : str(now.strftime('%M')),
        'b_second' : str(now.strftime('%S')),
        'b_dayNumber' : str(now.strftime('%d')),
        'b_month' : str(now.strftime('%m')),
        'b_year' : str(now.strftime('%Y')),
        'b_timeZone' : '-4',
        'cardsmanage' : 'soa',
        'UserID' : self.user_name,
        'Password' : self.password,
        'REMEMBERME' : 'on'
        }
        res = self.s.post(login_page, data=data)
        if res.text.find('End login error message') == -1:
            self.logged_in = True
        else:
            self.logged_in = False
        return res.text
    
    def load_history(self):
        # CSV Download
        dwld_page = 'https://online.americanexpress.com/myca/ofxdl/us/domesticDownload.do?request_type=authreg_ofxdownload'
        data = {
        'sorted_index' : '0',
        'Face' : 'en_US',
        'request_type' : 'authreg_ofxdownload', 
        'formatType' : '6',
        'appVerID' : 'CSV|0100',
        'cardSelected' : 'Y',
        'BPIndex' : '',
        'ApplID' : '',
        'logoutURL' : 'https://online.americanexpress.com/myca/logon/us/action?request_type=LogLogoffHandler&Face=en_US&inav=Logout',
        'ofxURL' : 'https://online.americanexpress.com/myca/ofxdl/us/domesticOptions.do?request_type=authreg_ofxdownload',
        'estmtQBURL' : 'https://online.americanexpress.com/myca/estmt/us/list.do?request_type=authreg_Statement',
        'Hidden' : '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~AAAAE1NlbGVjdGVkU29ydGVkSW5kZXgAAAAIrO0ABXQAATA=~~',
        'numAccts' : '<bean:write name="cardList" property="size"/>',
        'appID' : 'QACT',
        'value(timeFrame0)' : 'downloadDates',
        'value(cycleCut00)' : 'on',
        'value(cycleCut01)' : 'on',
        'value(cycleCut02)' : 'on',
        'value(cycleCut03)' : 'on',
        'value(cycleCut04)' : 'on',
        'value(cycleCut05)' : 'on',
        'value(cycleCut06)' : 'on',
        'value(cycleCut07)' : 'on',
        'value(cycleCut08)' : 'on',
        'value(cycleCut09)' : 'on',
        'value(cycleCut10)' : 'on',
        }
        hist = self.s.post(dwld_page, data=data)
        df = pd.read_csv(StringIO(hist.text), names=['date', 'ref', 'value', 'store', 'store_id'])
        df = df[[type(pd.to_datetime(t)) == pd.tslib.Timestamp for t in df.date]]
        df = df[df.value.isnull()==False]
        df.date = pd.to_datetime(df.date)
        return df