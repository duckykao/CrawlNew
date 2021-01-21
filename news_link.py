import numpy as np
import pandas as pd

# News Websites
anue_world = "https://news.cnyes.com/news/cat/wd_stock"
anue_taiwan = "https://news.cnyes.com/news/cat/tw_stock"
anue_china_HK = "https://news.cnyes.com/news/cat/cn_stock"
anue_root_url = "https://news.cnyes.com"
ec_international_1 = "https://ec.ltn.com.tw/list/international/1"
ec_international_2 = "https://ec.ltn.com.tw/list/international/2"
ec_international_3 = "https://ec.ltn.com.tw/list/international/3"
money_udn_world_1 = "https://money.udn.com/money/breaknews/1001/5588/1"
money_udn_world_2 = "https://money.udn.com/money/breaknews/1001/5588/2"
money_udn_world_3 = "https://money.udn.com/money/breaknews/1001/5588/3"
money_udn_china_1 = "https://money.udn.com/money/breaknews/1001/5589/1"
money_udn_china_2 = "https://money.udn.com/money/breaknews/1001/5589/2"
money_udn_china_3 = "https://money.udn.com/money/breaknews/1001/5589/3"

# sheet_name
sheetname = ["US","EU","APAC","Taiwan","EM","others"]

# Keywords
TW_keywords = ["台灣","台股"]
US_keywords = ["美國", "加拿大","川普","美股", "紐約", "芝加哥", "全美","Fed","美元指數","紐時","美商務部","美非農"]  
APAC_keywords = ["日本", "南韓", "韓國", "中國", "香港", "澳洲", "紐西蘭", "新加坡", "北京", "東京", "大陸", "新華社","日企","人民幣",
                "習近平","中共","港","人行"]  
EU_keywords = ["歐盟","奧地利","比利時","愛爾蘭","以色列","義大利","葡萄牙","西班牙","丹麥","芬蘭","法國","荷蘭","挪威","瑞典","瑞士","英國",
               "德國","倫敦"]
EM_keywords = ["巴西","智利","哥倫比亞","捷克","埃及","希臘","匈牙利","印度","印尼","馬來西亞",
                "墨西哥","秘魯","菲律賓","波蘭","卡達","俄羅斯","南非","泰國","土耳其","阿拉伯"]

All_keywords = TW_keywords + US_keywords + APAC_keywords + EU_keywords + EM_keywords

# change the news label from the website to our label or keyword list which is used to determine our label
Mapping = {'美股':"US", '國際政經':All_keywords, '歐亞股':APAC_keywords+EU_keywords, 
           '台股新聞':"Taiwan", '台灣政經':"Taiwan", '台股盤勢':"Taiwan",'台股':"Taiwan",
           '大陸政經':"APAC", 'A股':"APAC", '港股':"APAC", "兩岸":APAC_keywords+TW_keywords,
           'unsure':All_keywords,'國際':All_keywords, '國際股':All_keywords}

# From keywords in the mapping to our label
Reverse_Mapping = {}
for i in range(len(All_keywords)):
    count = 0
    if(i in np.arange(0, len(TW_keywords))): Reverse_Mapping['{}'.format(All_keywords[i])] = "Taiwan"
    count = len(TW_keywords)

    if(i in np.arange(count, count+len(US_keywords))): Reverse_Mapping['{}'.format(All_keywords[i])] = "US"
    count = count+len(US_keywords)

    if(i in np.arange(count, count+len(APAC_keywords))): Reverse_Mapping['{}'.format(All_keywords[i])] = "APAC"
    count = count+len(APAC_keywords)

    if(i in np.arange(count, count+len(EU_keywords))): Reverse_Mapping['{}'.format(All_keywords[i])] = "EU"
    count = count+len(EU_keywords)

    if(i in np.arange(count, count+len(EM_keywords))): Reverse_Mapping['{}'.format(All_keywords[i])] = "EM"
