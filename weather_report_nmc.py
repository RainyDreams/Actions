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
weather_template_id = os.environ.get("TEMPLATE_ID_NMC")

# 将OPEN_ID字符串转换为数组
openId_list = openId_str.split(",")

def get_weather():
    url = 'http://nmc.cn/rest/weather?stationid=54218'
    response = requests.get(url)
    data = json.loads(response.text)
    result = []
    if 'data' in data and 'real' in data['data']:
        real_data = data['data']['real']
        if 'weather' in real_data:
            weather_data = real_data['weather']
            if 'temperature' in weather_data:
                temperature_value = weather_data['temperature']
                result.append(temperature_value)
            else:
                result.append(None)
        else:
            result.append(None)
        
        if 'publish_time' in real_data:
            publish_time_value = real_data['publish_time']
            result.append(publish_time_value)
        else:
            result.append(None)

    return result

def get_access_token():
    # 获取access token的url
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}' \
        .format(appID.strip(), appSecret.strip())
    response = requests.get(url).json()
    print(response)
    access_token = response.get('access_token')
    return access_token

def send_weather(access_token, weather, openId):
    # touser 就是 openID
    # template_id 就是模板ID
    # url 就是点击模板跳转的url
    # data就按这种格式写，time和text就是之前{{time.DATA}}中的那个time，value就是你要替换DATA的值
    body = {
        "touser": openId.strip(),
        "template_id": weather_template_id.strip(),
        "url": "http://nmc.cn/publish/forecast/ANM/chifeng.html",
        "data": {
            "weather": {
                "value": weather[0]
            },
            "update": {
                "value": weather[1]
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
