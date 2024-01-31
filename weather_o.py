import os
import requests
import json
from bs4 import BeautifulSoup

# 从测试号信息获取
appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
# 收信人ID即 用户列表中的微信号
openId_str = os.environ.get("OPEN_ID")
# 天气预报模板ID
weather_template_id = os.environ.get("TEMPLATE_ID_ogimet")

# 将OPEN_ID字符串转换为数组
openId_list = openId_str.split(",")

def get_third_row(url):
    # 发送GET请求获取网页代码
    response = requests.get(url)
    html = response.text
    # 使用BeautifulSoup解析网页代码
    soup = BeautifulSoup(html, 'html.parser')
    # 找到table元素
    table = soup.find('table')
    # 找到第三行(tr)
    third_row = table.find_all('tr')[2]
    # 获取第三行的td数据，组成一个数组
    row_data = [cell.text.strip() for cell in third_row.find_all('td')]
    return row_data

def get_weather():
    from datetime import date
    today = date.today()
    year = today.year
    month = today.month
    day = today.day
    url = 'https://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=54218&ndays=1&ano={}&mes={}&day={}&hora=00&ord=REV&Send=Send'\
        .format(year,month,day)
    data = get_third_row(row)
    return data


def get_access_token():
    # 获取access token的url
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}' \
        .format(appID.strip(), appSecret.strip())
    response = requests.get(url).json()
    print(response)
    access_token = response.get('access_token')
    return access_token

def send_weather(access_token, weather, openId):
    from datetime import date
    today = date.today()
    year = today.year
    month = today.month
    day = today.day
    url = 'https://www.ogimet.com/cgi-bin/gsynres?lang=en&ind=54218&ndays=1&ano={}&mes={}&day={}&hora=00&ord=REV&Send=Send'\
        .format(year,month,day)
    body = {
        "touser": openId.strip(),
        "template_id": weather_template_id.strip(),
        "url": url,
        "data": {
            "Date": {
                "value": today
            },
            "Max_Temperature": {
                "value": weather[1]
            },
            "Min_Temperature": {
                "value": weather[2]
            },
            "Avg_Temperature": {
                "value": weather[3]
            },
            "Td_Avg": {
                "value": weather[4]
            },
            "Hr_Avg": {
                "value": weather[5]
            },
            "Dir_Wind": {
                "value": weather[6]
            },
            "Int_Wind": {
                "value": weather[7]
            },
            "Gust_Wind": {
                "value": weather[8]
            },
            "Pres_S_lev": {
                "value": weather[9]
            },
            "Prec": {
                "value": weather[10]
            },
            "Vis": {
                "value": weather[11]
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
    print(f"天气信息： {weather}")
    # 逐个推送消息
    for openId in openId_list:
        send_weather(access_token, weather, openId)

if __name__ == '__main__':
    weather_report()
