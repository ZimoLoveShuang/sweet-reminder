import requests
import math
import yaml
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.header import Header


# 读取yml配置
def getYmlConfig(yaml_file='config.yml'):
    file = open(yaml_file, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    config = yaml.load(file_data, Loader=yaml.FullLoader)
    return dict(config)


config = getYmlConfig()
application = config['application']
girlfriend = config['girlfriend']


# 获取天气信息，今天的和明天的
def getWeather(city, appid=application['weather']['appid'], appsecret=application['weather']['appsecret']):
    url = 'https://www.tianqiapi.com/api/?version=v1&city={city}&appid={appid}&appsecret={appsecret}'.format(city=city,
                                                                                                             appid=appid,
                                                                                                             appsecret=appsecret)
    res = requests.get(url)
    data = res.json()['data']
    return {
        'today': data[0],
        'tomorrow': data[1]
    }


# 获取土味情话，有时候很智障
def getSweetWord():
    url = 'https://api.lovelive.tools/api/SweetNothings/1/Serialization/Json'
    res = requests.get(url)
    return res.json()['returnObj'][0]


# 模板消息，有能力的话，可以自己修改这个模板
def getMessage():
    now = datetime.now()
    start = datetime.strptime(girlfriend['start_love_date'], "%Y-%m-%d")
    days = (now - start).days
    city = girlfriend['city']
    weather = getWeather(city=city)
    today = weather['today']
    tomorrow = weather['tomorrow']
    today_avg = (int(today['tem1'][:-1]) + int(today['tem2'][:-1])) / 2
    tomorrow_avg = (int(tomorrow['tem1'][:-1]) + int(tomorrow['tem2'][:-1])) / 2
    wdc = ''
    if today_avg > tomorrow_avg:
        wdc += '下降'
        wdc += str(abs(tomorrow_avg - today_avg)) + "℃"
    elif math.isclose(tomorrow_avg, today_avg):
        wdc += '保持不变'
    else:
        wdc += '上升'
        wdc += str(abs(tomorrow_avg - today_avg)) + "℃"
    return "❥(^_-) " + config['girlfriend'].get("nickname") + \
           "\n今天是 " + today['date'] + " " + today['week'] + \
           "\n" + girlfriend['date_msg'] % days + \
           "\n" + "\\(^o^)/ 温馨提示" + \
           "\n" + city + " 明日天气：" + tomorrow['wea'] + \
           "\n" + "气温：" + tomorrow['tem2'][:-1] + "/" + tomorrow['tem1'][:-1] + "℃" + \
           "\n" + "与今天相比，明天的平均气温将会：" + wdc + \
           "\n" + "(～￣▽￣)～ 穿衣建议：" + tomorrow['index'][3]['desc'] + \
           "\n" + "O(∩_∩)O 今夜情话" + \
           "\n" + getSweetWord() + \
           "\n" + "以上信息来自 " + girlfriend["sweet_nickname"] + " " + "(づ￣ 3￣)づ"


def sendQQMail(sender, receivers):
    mail_host = application['mail']['host']
    mail_port = application['mail']['port']
    mail_user = application['mail']['username']
    mail_pass = application['mail']['password']
    encoding = application['mail']['default-encoding']

    mail_msg = getMessage()
    print(mail_msg)
    message = MIMEText(mail_msg, 'plain', encoding)
    message['From'] = Header(sender, encoding)

    subject = application['name']
    message['Subject'] = Header(subject, 'utf-8')

    smtpObj = smtplib.SMTP_SSL(mail_host, mail_port)
    smtpObj.login(mail_user, mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())


def main_handler(event, context):
    try:
        sendQQMail(application['mail']['username'], girlfriend['mails'])
    except Exception as e:
        print('出现错误')
        raise e
    else:
        return 'success'


if __name__ == '__main__':
    print(main_handler({}, {}))
