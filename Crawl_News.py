import requests as req
from bs4 import BeautifulSoup
import time
import pandas as pd
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from news_link import *
import sys
sys.setrecursionlimit(1000000)
import numpy as np
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib

# https://blog.csdn.net/zhangpeterx/article/details/83502641 
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')  
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--headless')
chrome_options.add_argument('blink-settings=imagesEnabled=false')
chrome_options.add_argument('--disable-gpu')


# date
date = time.localtime(time.time())
if(date[3] == 11):
    AM_or_PM = "AM"
else:
    AM_or_PM = "PM"

date = "{}-{}-{}".format(date[0],str(date[1]).zfill(2),str(date[2]).zfill(2))

def Anue(anue, root_url, date):
    # https://stackoverflow.com/questions/35286094/how-to-close-the-whole-browser-window-by-keeping-the-webdriver-active
    browser = webdriver.Chrome(options=chrome_options)
    browser.get(anue)
    count = 1
    print("Crawling webpage : Anue-{}".format(anue.split("/")[-1]))
    while(count):
        if(count == 1):
            browser.execute_script("window.scrollTo(0, 5000)")
            soup = BeautifulSoup(browser.page_source, "html.parser")
            article = soup.select("._1Zdp")
            arr = []
            no_newer_news = 0
            for art in article:
                div = BeautifulSoup(str(art), "html.parser").select("div")
                datetime = BeautifulSoup(str(div[0]), "html.parser").select("time")[0]['datetime'].split("T")[0]
                if(datetime < date):
                    no_newer_news = 1
                    break
                x = [datetime, div[1].string, art['title'], root_url+art['href']]
                arr.append(x)
            if(len(arr) == 0):
                if(no_newer_news):
                    print("Anue {} : has no newer_news of day {}".format(anue.split("/")[-1], date))
                else:
                    with open('page_source.txt', 'w') as f:
                        f.write(str(article))
                    print("Anue {} : Didn't fetch the news correctly".format(anue.split("/")[-1]))
                    print("================ Re-Fetching the webpage ================")
                    return False

            df = pd.DataFrame(arr, columns=["date", "type", "title", "href"])
            count = count -1
    #print(df)
    browser.quit()
    return df

def EC_International(ec_international, date):
    res = req.get(ec_international)
    soup = BeautifulSoup(res.text, "html.parser")
    href = soup.select(".list li a")
    title = soup.select(".list li a p")
    arr = []
    no_newer_news = 0
    print("Crawling webpage : EC_International_{}".format(format(ec_international.split("/")[-1])))
    for i in range(len(title)):
        datetime = soup.select(".list li a span")[i].string.split(" ")[0].split("/")
        datetime = "{}-{}-{}".format(datetime[0],datetime[1],datetime[2])
        if(datetime < date):
            no_newer_news = 1
            break
        x = [datetime, "unsure",title[i].string, href[i]['href']]
        arr.append(x)
    
    if(len(arr) == 0):
        if(no_newer_news):
                    print("EC_International {} : has no newer_news of day {}".format(ec_international.split("/")[-1], date))
        else:
            print("EC_International-{} : Didn't fetch the news correctly".format(ec_international.split("/")[-1]))
            print("================ Re-Fetching the webpage ================")
            return False

    df = pd.DataFrame(arr, columns=["date", "type", "title", "href"])
    return df

def Money_udn(money_udn, date):
    res = req.get(money_udn)
    soup = BeautifulSoup(res.text, "html.parser")
    article = soup.select("td a")
    type_ = soup.select("td.only_web")
    arr = []

    if money_udn.split("/")[-2] == "5588":
        print("Crawling webpage : Money_udn-world_{}".format(format(money_udn.split("/")[-1])))
    else:
        print("Crawling webpage : Money_udn-china_{}".format(format(money_udn.split("/")[-1])))
    
    no_newer_news = 0
    for i in range(60):
        datetime = type_[2*i+1].string.split(" ")[0].split("/")
        datetime = "2020-{}-{}".format(datetime[0], datetime[1])
        if(datetime < date):
            no_newer_news = 1
            break
            
        x = [datetime, type_[2*i].string, article[i].string, article[i]['href']]
        arr.append(x)

    if(len(arr) == 0):
        if(no_newer_news):
            print("Money_udn {} : has no newer_news of day {}".format(money_udn.split("/")[-1], date))
        else:
            print("Money_udn-{} : Didn't fetch the news correctly".format(money_udn.split("/")[-1]))
            print("================ Re-Fetching the webpage ================")
            return False

    df = pd.DataFrame(arr, columns=["date", "type", "title", "href"])
    return df, no_newer_news

def Change_News_Label_2_Our_Label(News):
    for index in range(len(News['title'])):
        x = Mapping['{}'.format(News['type'][index])]
        if(type(x).__name__ == 'str'):
            News['type'][index] = x
        else:
            if_others = True
            for terms in x:
                if(terms in str(News['title'][index])):
                    News['type'][index] = Reverse_Mapping['{}'.format(terms)]
                    if_others = False
                    break
            if(if_others):
                News['type'][index] = "others"

def News_2_Excel(News, sheetname, date, AM_or_PM):

    path = "put your own path/CrawlNews/News/"
    excel_filename = path + "{}-{}-News.xlsx".format(date, AM_or_PM)

    US_df = News[News["type"] == sheetname[0]]
    EU_df = News[News["type"] == sheetname[1]]
    APAC_df = News[News["type"] == sheetname[2]]
    TW_df = News[News["type"] == sheetname[3]]
    EM_df = News[News["type"] == sheetname[4]]
    Other_df = News[News["type"] == sheetname[5]]

    with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
        US_df.to_excel(writer, index=False, encoding="utf_8_sig", sheet_name=sheetname[0])
        EU_df.to_excel(writer, index=False, encoding="utf_8_sig", sheet_name=sheetname[1])
        APAC_df.to_excel(writer, index=False, encoding="utf_8_sig", sheet_name=sheetname[2])
        TW_df.to_excel(writer, index=False, encoding="utf_8_sig", sheet_name=sheetname[3])
        EM_df.to_excel(writer, index=False, encoding="utf_8_sig", sheet_name=sheetname[4])
        Other_df.to_excel(writer, index=False, encoding="utf_8_sig", sheet_name=sheetname[5])
        for i in range(6):
            workbook  = writer.book
            cell_format = workbook.add_format({'align':'center'})
            worksheet = writer.sheets[sheetname[i]]
            worksheet.set_column('A:A',10,cell_format)
            worksheet.set_column('B:B',7,cell_format)
            worksheet.set_column('C:C',80,cell_format)
            worksheet.set_column('D:D',55,cell_format)

def Send_Daily_News_To_Mail(date, AM_or_PM):

    path = "put your own path/CrawlNews/News/"
    excel_filename = path + "{}-{}-News.xlsx".format(date, AM_or_PM)

    # Account infomation load
    account = {'Account':'colladailynews@gmail.com', 'Password':'colla70847711'}
    gmailUser = account['Account']
    gmailPasswd = account['Password']
    recipients = ['duckykao010708@gmail.com','t3479567@gmail.com']
    emails = [t.split(',') for t in recipients]

    # Create message
    message = MIMEMultipart()
    message['Subject'] = 'News of {}'.format(date)
    message['From'] = gmailUser
    message['To'] = ','.join(recipients)

    # Mail content
    message.attach(MIMEText('{} News!'.format(date), 'plain', 'utf-8'))

    # File
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(excel_filename, "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(excel_filename))
    message.attach(part)

    smtp = smtplib.SMTP("smtp.gmail.com:587")
    smtp.ehlo()
    smtp.starttls()
    smtp.login(gmailUser, gmailPasswd)

    smtp.sendmail(message['From'], recipients, message.as_string())
    print('Send mails OK!')

def Crawling():

    # Initialize DataFrame for each website
    df_anue_world         = pd.DataFrame([], columns=["date", "type", "title", "href"])
    df_anue_taiwan        = pd.DataFrame([], columns=["date", "type", "title", "href"])
    df_anue_china_HK      = pd.DataFrame([], columns=["date", "type", "title", "href"])
    df_ec_international_1 = pd.DataFrame([], columns=["date", "type", "title", "href"])
    df_ec_international_2 = pd.DataFrame([], columns=["date", "type", "title", "href"])
    df_ec_international_3 = pd.DataFrame([], columns=["date", "type", "title", "href"])
    df_money_udn_world_1  = pd.DataFrame([], columns=["date", "type", "title", "href"])
    df_money_udn_world_2  = pd.DataFrame([], columns=["date", "type", "title", "href"])
    df_money_udn_world_3  = pd.DataFrame([], columns=["date", "type", "title", "href"])
    df_money_udn_china_1  = pd.DataFrame([], columns=["date", "type", "title", "href"])
    df_money_udn_china_2  = pd.DataFrame([], columns=["date", "type", "title", "href"])
    df_money_udn_china_3  = pd.DataFrame([], columns=["date", "type", "title", "href"])

    print("Start Fetching {}-{} News".format(date,AM_or_PM))
    while(True):
        df_anue_world = Anue(anue_world, anue_root_url, date)
        if(type(df_anue_world).__name__ == "DataFrame"): break
    while(True):
        df_anue_taiwan = Anue(anue_taiwan, anue_root_url, date)
        if(type(df_anue_taiwan).__name__ == "DataFrame"): break
    while(True):
        df_anue_china_HK = Anue(anue_china_HK, anue_root_url, date)
        if(type(df_anue_china_HK).__name__ == "DataFrame"): break
    while(True):
        df_ec_international_1 = EC_International(ec_international_1, date)
        if(type(df_ec_international_1).__name__ == "DataFrame"): break
    while(True):
        df_ec_international_2 = EC_International(ec_international_2, date)
        if(type(df_ec_international_2).__name__ == "DataFrame"): break
    while(True):
        df_ec_international_3 = EC_International(ec_international_3, date)
        if(type(df_ec_international_3).__name__ == "DataFrame"): break
    
    while(True):
        df_money_udn_world_1, world_check_page2 = Money_udn(money_udn_world_1, date)
        if(type(df_money_udn_world_1).__name__ == "DataFrame"): break
    if(world_check_page2 == 0):
        while(True):
            df_money_udn_world_2, world_check_page3 = Money_udn(money_udn_world_2, date)
            if(type(df_money_udn_world_2).__name__ == "DataFrame"): break
        if(world_check_page3 == 0):
            while(True):
                df_money_udn_world_3, world_check_page4 = Money_udn(money_udn_world_3, date)
                if(type(df_money_udn_world_3).__name__ == "DataFrame"): break
            world_check_page3 = 1
        world_check_page2 = 1
    
    while(True):
        df_money_udn_china_1, china_check_page2 = Money_udn(money_udn_china_1, date)
        if(type(df_money_udn_china_1).__name__ == "DataFrame"): break
    if(china_check_page2 == 0):
        while(True):
            df_money_udn_china_2, china_check_page3 = Money_udn(money_udn_china_2, date)
            if(type(df_money_udn_china_2).__name__ == "DataFrame"): break
        if(china_check_page3 == 0):
            while(True):
                df_money_udn_china_3, china_check_page4 = Money_udn(money_udn_china_3, date)
                if(type(df_money_udn_china_3).__name__ == "DataFrame"): break
            china_check_page3 = 1
        china_check_page2 = 1
    
    # concat all all news from different website
    frames = [df_anue_world, df_anue_taiwan, df_anue_china_HK, 
              df_ec_international_1, df_ec_international_2, df_ec_international_3, 
              df_money_udn_world_1, df_money_udn_world_2, df_money_udn_world_3, 
              df_money_udn_china_1, df_money_udn_china_2, df_money_udn_china_3]
    
    total_df = pd.concat(frames, ignore_index=True)
    return total_df

def main():
    
    # get the dataframe 
    total_df = Crawling()
    # change the news label from websites to our own label
    Change_News_Label_2_Our_Label(total_df)
    # store the news to excel
    News_2_Excel(total_df, sheetname, date, AM_or_PM)
    # Send Excel to user
    Send_Daily_News_To_Mail(date, AM_or_PM)

    # save to pickle file
    path = "put your own path/CrawlNews/News/"
    total_df.to_pickle(path + "{}-{}-News".format(date,AM_or_PM))

if __name__ == '__main__':
    main()


# https://stackoverflow.com/questions/8856117/how-to-send-email-to-multiple-recipients-using-python-smtplib
