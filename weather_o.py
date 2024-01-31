import os
import requests
import json
from bs4 import BeautifulSoup
import datetime 

appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
openId_str = os.environ.get("OPEN_ID")
weather_template_id = os.environ.get("TEMPLATE_ID_OGIMET")
uid = weather_template_id.strip() or "ljryQcnRHQXQGWUGv8i8zoGsOp4AUKpYiiHa28eVSDQ"
openId_list = openId_str.split(",")

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
today_str = today.strftime("%Y年%m月%d日")
year = today.year
month = today.month
day = today.day
_y = tomorrow.year
_m = tomorrow.month
_d = tomorrow.day

url_ = 'https://www.ogimet.com/cgi-bin/gsynres?ind=54218&lang=en&decoded=yes&ndays=2&ano={}&mes={}&day={}&hora=00'\
    .format(_y,_m,_d)

def get_weather():
    # 发送GET请求获取网页代码
    response = requests.get(url_)
    html = response.text
    # 使用BeautifulSoup解析网页代码
    soup = BeautifulSoup(html, 'html.parser')
    # 找到所有的table元素
    tables = soup.find_all('table')
    if len(tables) < 3:
        raise ValueError("网页中至少需要3个table元素")
    target_table = tables[2]
    # 找到第三行(tr)
    third_row = target_table.find_all('tr')[1]
    # 获取第三行的td数据，组成一个数组
    row_data = [cell.text.strip() for cell in third_row.find_all('td')]
    print(row_data)
    return row_data

def get_access_token():
    # 获取access token的url
    urlW = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}' \
        .format(appID.strip(), appSecret.strip())
    response = requests.get(urlW).json()
    print(response)
    access_token = response.get('access_token')
    return access_token

def send_weather(access_token, weather, openId):
    body = {
        "touser": openId.strip(),
        "template_id": uid,
        "url": url_,
        "data": {
            "Date": {
                "value": weather[0] + " " +  weather[1] + " UTC"
            },
            "T": {
                "value": weather[2]
            },
            "Td": {
                "value": weather[3]
            },
            "Hr": {
                "value": weather[4] + "%"
            },
            "T_max": {
                "value": weather[5]
            },
            "T_min": {
                "value": weather[6]
            },
            "ddd": {
                "value": weather[7]
            },
            "ff": {
                "value": weather[8] + "(kmh)"
            },
            "Gust": {
                "value": weather[9] + "(kmh)"
            },
            "P0": {
                "value": weather[10] + "(hPa)"
            },
            "P_sea": {
                "value": weather[11] + "(hPa)"
            },
            "P": {
                "value": weather[12] + "(Tnd)"
            },
            "Prec": {
                "value": weather[13] + "(mm)"
            },
            "Vis": {
                "value": weather[14] + "(km)"
            }
        }
    }
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(access_token)
    print(requests.post(url, json.dumps(body)).text)

def weather_report():
    # 获取access_token
    access_token = get_access_token()
    # 获取天气
    weather = get_weather()
    print(weather)
    # 逐个推送消息
    for openId in openId_list:
        send_weather(access_token, weather, openId)

if __name__ == '__main__':
    weather_report()
