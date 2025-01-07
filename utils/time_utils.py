import pytz
from datetime import datetime

def convert_utc_to_beijing(utc_time_str):
    """将UTC时间字符串转换为北京时间"""
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")
    utc_time = utc_time.replace(tzinfo=pytz.UTC)
    beijing_tz = pytz.timezone('Asia/Shanghai')
    beijing_time = utc_time.astimezone(beijing_tz)
    return beijing_time

def get_beijing_now():
    """获取北京当前时间"""
    beijing_tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(beijing_tz) 