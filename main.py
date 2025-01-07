import argparse
import os
from utils.client import get_client_profile, create_credential
from utils.config import (
    load_accounts, load_wechat_config, load_wechat_send_config, 
    load_email_config, load_alert_config, load_service_regions
)
from monitoring_services.cvm_service import CVMService
from monitoring_services.cbs_service import CBSService
from monitoring_services.domain_service import DomainService
from support_services.tag_service import TagService
from support_services.wechat_service import WeChatService
from support_services.email_service import EmailService
from monitoring_services.billing_service import BillingService
from monitoring_services.lighthouse_service import LighthouseService
from support_services.database_service import DatabaseService
from dotenv import load_dotenv
from utils.alert_utils import filter_resources_by_days
from utils.log_utils import setup_logger

# 加载环境变量
load_dotenv()

# 服务类型定义
SERVICE_TYPES = {
    # 资源类服务
    'RESOURCE_SERVICES': {
        # 需要region的服务
        'REGIONAL': {
            'CVM': {
                'regions': None,  # 将在运行时从配置加载
                'service_class': CVMService
            },
            'Lighthouse': {
                'regions': None,  # 将在运行时从配置加载
                'service_class': LighthouseService
            },
            'CBS': {
                'regions': None,  # 将在运行时从配置加载
                'service_class': CBSService
            }
        },
        # 不需要region的服务
        'GLOBAL': {
            'Domain': DomainService
        }
    },
    # 账单类服务
    'BILLING_SERVICES': {
        'Billing': {
            'service_class': BillingService,
            'region': None  # 将在运行时从配置加载
        }
    }
}

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='腾讯云资源和账单信息查询工具')
    parser.add_argument(
        '--mode', 
        choices=['all', 'resources', 'billing'],
        default='all',
        help='输出模式：all=全部信息，resources=仅资源信息，billing=仅账单信息'
    )
    return parser.parse_args()

def get_regional_resources(account_info, client_profile):
    """获取需要region的资源"""
    cred = create_credential(account_info["secret_id"], account_info["secret_key"])
    all_resources = {
        service_name: [] 
        for service_name in SERVICE_TYPES['RESOURCE_SERVICES']['REGIONAL'].keys()
    }
    
    # 遍历每个需要region的服务
    for service_name, service_info in SERVICE_TYPES['RESOURCE_SERVICES']['REGIONAL'].items():
        print(f"\n获取 {service_name} 资源...")
        
        # 遍历每个region
        for region in service_info['regions']:
            print(f"正在获取 {region} 区域的资源...")
            
            # 初始化服务
            service = service_info['service_class'](cred, client_profile, region)
            
            # 获取资源（根据服务类型调用相应的方法）
            if service_name == 'CVM':
                resources = service.get_instances()
            elif service_name == 'Lighthouse':
                resources = service.get_instances()
            elif service_name == 'CBS':
                resources = service.get_disks()
                
            # 添加region信息到资源中
            for resource in resources:
                resource['Region'] = region
            
            all_resources[service_name].extend(resources)
    
    return all_resources

def get_global_resources(account_info, client_profile):
    """获取不需要region的资源"""
    cred = create_credential(account_info["secret_id"], account_info["secret_key"])
    all_resources = {}
    
    for service_name, service_class in SERVICE_TYPES['RESOURCE_SERVICES']['GLOBAL'].items():
        print(f"\n获取 {service_name} 资源...")
        # 使用默认region
        service = service_class(cred, client_profile, "ap-guangzhou")
        
        if service_name == 'Domain':
            all_resources[service_name] = service.get_domains()
            
    return all_resources

def get_billing_info(account_info, client_profile):
    """获取账单相关信息"""
    cred = create_credential(account_info["secret_id"], account_info["secret_key"])
    billing_info = {}
    
    for service_name, service_info in SERVICE_TYPES['BILLING_SERVICES'].items():
        service = service_info['service_class'](
            cred, 
            client_profile,
            service_info['region']
        )
        
        if service_name == 'Billing':
            billing_info['balance'] = service.get_account_balance()
            billing_info['bill_details'] = service.get_monthly_bill()
            
    return billing_info

def display_billing_info(account_name, billing_info):
    """显示账单信息"""
    messages = [f"📢腾讯云 {account_name} 账单信息\n"]
    
    messages.extend([
        "=== 账户余额 ===",
        f"当前余额: {billing_info['balance']}元\n",
        "=== 本月账单 ==="
    ])
    
    for project_name, details in billing_info['bill_details'].items():
        messages.append(f"\n项目: {project_name}")
        for service_name, costs in details["services"].items():
            messages.append(f"{service_name}: {costs['RealTotalCost']}元")
    
    print("\n".join(messages))
    return "\n".join(messages)

def main():
    # 设置日志记录器
    logger = setup_logger()
    
    # 解析命令行参数
    args = parse_args()
    
    # 从环境变量加载配置
    accounts = load_accounts()
    client_profile = get_client_profile()
    alert_config = load_alert_config()
    wechat_bots = load_wechat_config()
    wechat_send_config = load_wechat_send_config()
    email_config = load_email_config()
    service_regions = load_service_regions()
    
    # 更新服务配置中的区域信息
    for service in SERVICE_TYPES['RESOURCE_SERVICES']['REGIONAL'].values():
        service['regions'] = service_regions['resources']
    SERVICE_TYPES['BILLING_SERVICES']['Billing']['region'] = service_regions['billing']
    
    # 初始化通知服务
    wechat_service = WeChatService(wechat_bots) if alert_config['enable_wechat'] else None
    email_service = EmailService(email_config) if alert_config['enable_email'] else None
    
    # 数据库配置
    db_config = {
        'enable_db': os.getenv('ENABLE_DATABASE', 'false').lower() == 'true',
        'database': os.getenv('DB_DATABASE'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT', '3306')
    }
    
    # 初始化数据库服务
    db_service = DatabaseService(db_config)
    
    for account_name, account_info in accounts.items():
        logger.info(f"腾讯云 {account_name} 账号信息")
        
        # 获取资源信息
        if args.mode in ['all', 'resources']:
            # 获取需要region的资源
            regional_resources = get_regional_resources(account_info, client_profile)
            
            # 获取不需要region的资源
            global_resources = get_global_resources(account_info, client_profile)
            
            # 显示结果（显示所有资源）
            display_results(account_name, regional_resources, global_resources)
            
            # 处理资源告警
            if any([alert_config['enable_wechat'], alert_config['enable_email']]):
                # 过滤需要告警的资源（只用于告警）
                filtered_regional_resources = {}
                for service_name, resources in regional_resources.items():
                    if service_name in ['CVM', 'CBS', 'Lighthouse']:
                        filtered_regional_resources[service_name] = filter_resources_by_days(
                            resources, alert_config
                        )
                    else:
                        filtered_regional_resources[service_name] = resources
                
                filtered_global_resources = {}
                for service_name, resources in global_resources.items():
                    if service_name == 'Domain':
                        filtered_global_resources[service_name] = filter_resources_by_days(
                            resources, alert_config
                        )
                    else:
                        filtered_global_resources[service_name] = resources
                
                # 检查是否有需要告警的资源
                has_alert_resources = False
                for resources in filtered_regional_resources.values():
                    if resources:
                        has_alert_resources = True
                        break
                for resources in filtered_global_resources.values():
                    if resources:
                        has_alert_resources = True
                        break

                # 在specific模式下，显示告警资源状态
                if alert_config['resource_alert_mode'] == 'specific':
                    if has_alert_resources:
                        logger.info(f"发现剩余 {alert_config['resource_alert_days']} 天内即将到期的资源，准备发送告警...")
                    else:
                        logger.info(f"未发现剩余 {alert_config['resource_alert_days']} 天内即将到期的资源，跳过告警发送。")
                
                # 发送企业微信通知
                if alert_config['enable_wechat'] and wechat_service:
                    message = wechat_service.format_resource_message(
                        account_name, filtered_regional_resources, filtered_global_resources
                    )
                    
                    if message:  # 只有在有需要告警的资源时才发送
                        # 根据配置决定发送方式
                        if wechat_send_config["send_mode"] == "all":
                            results = wechat_service.send_message(message)
                        else:
                            results = wechat_service.send_message(
                                message,
                                bot_names=wechat_send_config["bot_names"]
                            )
                        
                        # 输出发送结果
                        for bot_name, success in results.items():
                            status = "成功" if success else "失败"
                            logger.info(f"[资源告警] 企业微信通知发送到 {bot_name}: {status}")
                
                # 发送邮件通知
                if alert_config['enable_email'] and email_service:
                    subject = f"腾讯云 {account_name} 资源到期提醒"
                    content = email_service.format_resource_message(
                        account_name, filtered_regional_resources, filtered_global_resources
                    )
                    
                    if content:  # 只有在有需要告警的资源时才发送
                        if email_service.send_email(subject, content):
                            logger.info("[资源告警] 邮件通知发送成功")
                        else:
                            logger.error("[资源告警] 邮件通知发送失败")
            
            # 写入数据库（使用原始未过滤的资源）
            db_service.insert_cvm_instances(regional_resources.get('CVM', []))
            db_service.insert_lighthouse_instances(regional_resources.get('Lighthouse', []))
            db_service.insert_cbs_disks(regional_resources.get('CBS', []))
            db_service.insert_domains(global_resources.get('Domain', []))
        
        # 获取账单信息（账单告警不受资源告警天数的影响）
        if args.mode in ['all', 'billing']:
            # 获取账单信息
            billing_info = get_billing_info(account_info, client_profile)
            
            # 显示账单信息
            message = display_billing_info(account_name, billing_info)
            
            # 发送企业微信通知
            if alert_config['enable_wechat'] and wechat_service:
                # 根据配置决定发送方式
                if wechat_send_config["send_mode"] == "all":
                    results = wechat_service.send_message(message)
                else:
                    results = wechat_service.send_message(
                        message,
                        bot_names=wechat_send_config["bot_names"]
                    )
                
                # 输出发送结果
                for bot_name, success in results.items():
                    status = "成功" if success else "失败"
                    logger.info(f"[账单告警] 企业微信通知发送到 {bot_name}: {status}")
            
            # 发送邮件通知
            if alert_config['enable_email'] and email_service:
                subject = f"腾讯云 {account_name} 账单信息"
                if email_service.send_email(subject, message):
                    logger.info("[账单告警] 邮件通知发送成功")
                else:
                    logger.error("[账单告警] 邮件通知发送失败")
            
            # 写入数据库
            db_service.insert_billing_info(account_name, billing_info['balance'], billing_info['bill_details'])
    
    # 关闭数据库连接
    db_service.close()

def display_results(account_name, regional_resources, global_resources):
    """按区域显示资源信息"""
    messages = [f"📢腾讯云 {account_name} 资源到期提醒\n"]
    
    # 处理CVM资源
    cvm_resources = []
    for resources in regional_resources.values():
        if isinstance(resources, list):
            for resource in resources:
                if resource.get('Type') == 'CVM':
                    cvm_resources.append(resource)
    
    if cvm_resources:
        messages.append("=== 云服务器 ===")
        for resource in cvm_resources:
            messages.extend([
                f"名称: {resource['InstanceName']}",
                f"项目: {resource.get('ProjectName', '未知项目')}",
                f"区域: {resource['Zone']}",
                f"到期时间: {resource['ExpiredTime']}",
                f"剩余天数: {resource['DifferDays']}天\n"
            ])
    
    # 处理轻量应用服务器资源
    lighthouse_resources = []
    for resources in regional_resources.values():
        if isinstance(resources, list):
            for resource in resources:
                if resource.get('Type') == 'Lighthouse':
                    lighthouse_resources.append(resource)
    
    if lighthouse_resources:
        messages.append("=== 轻量应用服务器 ===")
        for resource in lighthouse_resources:
            messages.extend([
                f"名称: {resource['InstanceName']}",
                f"区域: {resource['Zone']}",
                f"到期时间: {resource['ExpiredTime']}",
                f"剩余天数: {resource['DifferDays']}天\n"
            ])
    
    # 处理CBS资源
    cbs_resources = []
    for resources in regional_resources.values():
        if isinstance(resources, list):
            for resource in resources:
                if resource.get('Type') == 'CBS':
                    cbs_resources.append(resource)
    
    if cbs_resources:
        messages.append("=== 云硬盘 ===")
        for resource in cbs_resources:
            messages.extend([
                f"名称: {resource['DiskName']}",
                f"项目: {resource['ProjectName']}",
                f"区域: {resource['Zone']}",
                f"到期时间: {resource['ExpiredTime']}",
                f"剩余天数: {resource['DifferDays']}天\n"
            ])
    
    print("\n".join(messages))

if __name__ == "__main__":
    main()
