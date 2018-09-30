import sys
import os
import requests
import time
from dateutil import parser
from pytz import timezone
from datetime import datetime, timedelta
import urllib
import subprocess
import io
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
        dwld_page1='https://global.americanexpress.com/myca/intl/download/emea/download.do?request_type=&Face=de_DE&sorted_index=0&omnlogin=de_lilo_myca'
        dwld_page='https://global.americanexpress.com/myca/intl/download/emea/downloadofx.do?request_type=&Face=de_DE'
        headers={
                'content-type': 'application/x-www-form-urlencoded',
        }
        data = [
                ('Format', 'CSV'),
                ('downloadFormat', 'on'),
        ]
        hist = self.s.get(dwld_page1)
        bs_data = [ (x['name'],x['value']) for x in BeautifulSoup(hist.text, "lxml").find('form', {'name': 'DownloadForm'}).findAll('input') if 'value' in x.attrs]
        bs_data = [ (x['name'],x['value']) for x in BeautifulSoup(hist.text, "lxml").findAll('input', {'name': 'selectradio'}) if 'value' in x.attrs] + bs_data
        data= [x for x in bs_data if x[0] not in [x[0] for x in data]] + data
        hist = self.s.post(dwld_page, data=data, headers=headers)
        df = pd.read_csv(io.StringIO(hist.text), names=['date', 'ref', 'value', 'store', 'store_id'], index_col=False)
        df = df[[type(pd.to_datetime(t)) == pd.Timestamp for t in df.date]]
        df = df[df.value.isnull()==False]
        df.date = pd.to_datetime(df.date)
        return df
