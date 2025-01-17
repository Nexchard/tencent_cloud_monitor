import os
from dotenv import load_dotenv

def load_accounts():
    """从.env文件加载账号配置"""
    load_dotenv()
    accounts = {}
    
    # 遍历环境变量查找所有账号配置
    i = 1
    while True:
        account_name = os.getenv(f'ACCOUNT{i}_NAME')
        if not account_name:
            break
            
        accounts[account_name] = {
            "secret_id": os.getenv(f'ACCOUNT{i}_SECRET_ID'),
            "secret_key": os.getenv(f'ACCOUNT{i}_SECRET_KEY')
        }
        i += 1
    
    return accounts 

def load_wechat_config():
    """加载企业微信配置"""
    load_dotenv()
    bots = {}
    
    # 遍历环境变量查找所有机器人配置
    i = 1
    while True:
        bot_name = os.getenv(f'WECHAT_BOT{i}_NAME')
        if not bot_name:
            break
            
        bots[bot_name] = {
            "webhook_url": os.getenv(f'WECHAT_BOT{i}_WEBHOOK')
        }
        i += 1
    
    return bots 

def load_wechat_send_config():
    """加载企业微信发送配置"""
    load_dotenv()
    return {
        "send_mode": os.getenv('WECHAT_SEND_MODE', 'all'),
        "bot_names": [
            name.strip() 
            for name in os.getenv('WECHAT_TARGET_BOTS', '').split(',')
            if name.strip()
        ] if os.getenv('WECHAT_TARGET_BOTS') else None
    } 

def load_email_config():
    """加载邮件配置"""
    load_dotenv()
    return {
        'smtp_server': os.getenv('EMAIL_SMTP_SERVER'),
        'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', 465)),
        'sender': os.getenv('EMAIL_SENDER'),
        'password': os.getenv('EMAIL_PASSWORD'),
        'receivers': [
            email.strip() 
            for email in os.getenv('EMAIL_RECEIVERS', '').split(',')
            if email.strip()
        ],
        'use_ssl': os.getenv('EMAIL_USE_SSL', 'true').lower() == 'true'
    } 

def load_alert_config():
    """加载告警配置"""
    return {
        'enable_email': os.getenv('ENABLE_EMAIL_ALERT', 'false').lower() == 'true',
        'enable_wechat': os.getenv('ENABLE_WECHAT_ALERT', 'false').lower() == 'true',
        'enable_yunzhijia': os.getenv('ENABLE_YUNZHIJIA_ALERT', 'false').lower() == 'true',
        'resource_alert_mode': os.getenv('RESOURCE_ALERT_MODE', 'all'),
        'resource_alert_days': int(os.getenv('RESOURCE_ALERT_DAYS', '65'))
    } 

def load_service_regions():
    """加载服务区域配置"""
    load_dotenv()
    return {
        'billing': os.getenv('BILLING_SERVICE_REGION', 'ap-guangzhou'),
        'resources': [
            region.strip() 
            for region in os.getenv('RESOURCE_SERVICE_REGIONS', 'ap-guangzhou').split(',')
            if region.strip()
        ]
    } 

def load_yunzhijia_config():
    """加载云之家配置"""
    load_dotenv()
    bots = {}
    
    # 遍历环境变量查找所有机器人配置
    i = 1
    while True:
        bot_name = os.getenv(f'YUNZHIJIA_BOT{i}_NAME')
        if not bot_name:
            break
            
        bots[bot_name] = {
            "webhook_url": os.getenv(f'YUNZHIJIA_BOT{i}_WEBHOOK')
        }
        i += 1
    
    return bots

def load_yunzhijia_send_config():
    """加载云之家发送配置"""
    load_dotenv()
    return {
        "send_mode": os.getenv('YUNZHIJIA_SEND_MODE', 'all'),
        "bot_names": [
            name.strip() 
            for name in os.getenv('YUNZHIJIA_TARGET_BOTS', '').split(',')
            if name.strip()
        ] if os.getenv('YUNZHIJIA_TARGET_BOTS') else None
    } 