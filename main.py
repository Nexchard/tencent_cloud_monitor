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
from monitoring_services.ssl_service import SSLService

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
            'Domain': DomainService,
            'SSL': SSLService
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
    # 修改数据结构，使用区域作为第一层键
    all_resources = {}
    
    # 遍历每个需要region的服务
    for service_name, service_info in SERVICE_TYPES['RESOURCE_SERVICES']['REGIONAL'].items():
        print(f"\n获取 {service_name} 资源...")
        
        # 遍历每个region
        for region in service_info['regions']:
            print(f"正在获取 {region} 区域的资源...")
            
            # 初始化区域的资源字典
            if region not in all_resources:
                all_resources[region] = {}
            
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
            
            # 将资源存储到对应区域的服务类型下
            all_resources[region][service_name] = resources
    
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
        elif service_name == 'SSL':
            all_resources[service_name] = service.get_certificates()
            
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
            print(f"\n处理账号: {account_name}")
            
            # 获取区域资源
            regional_resources = get_regional_resources(account_info, client_profile)
            # 获取全局资源
            global_resources = get_global_resources(account_info, client_profile)
            
            # 打印调试信息
            print(f"\n告警模式配置:")
            print(f"RESOURCE_ALERT_MODE: {os.getenv('RESOURCE_ALERT_MODE', 'all')}")
            print(f"RESOURCE_ALERT_DAYS: {os.getenv('RESOURCE_ALERT_DAYS', '65')}")
            
            # SSL证书过滤前数量
            ssl_count_before = len(global_resources.get('SSL', []))
            
            alert_mode = os.getenv("RESOURCE_ALERT_MODE", "all")
            alert_days = int(os.getenv("RESOURCE_ALERT_DAYS", "65"))
            
            if alert_mode == "specific":
                # 过滤区域资源
                for region, region_resources in regional_resources.items():
                    regional_resources[region] = {}
                    for service_name, resources in region_resources.items():
                        if service_name in ['CVM', 'CBS', 'Lighthouse']:
                            regional_resources[region][service_name] = filter_resources_by_days(
                                resources, 
                                alert_days
                            )
                        else:
                            regional_resources[region][service_name] = resources
                
                # 过滤全局资源
                for resource_type in global_resources:
                    global_resources[resource_type] = filter_resources_by_days(
                        global_resources[resource_type], 
                        alert_days
                    )
                    
                # SSL证书过滤后数量
                ssl_count_after = len(global_resources.get('SSL', []))
                print(f"\nSSL证书过滤情况:")
                print(f"过滤前数量: {ssl_count_before}")
                print(f"过滤后数量: {ssl_count_after}")
            
            # 显示结果
            display_results(account_name, regional_resources, global_resources)
            
            # 处理资源告警
            if any([alert_config['enable_wechat'], alert_config['enable_email']]):
                # 根据告警模式决定是否过滤资源
                filtered_regional_resources = {}
                filtered_global_resources = {}
                
                if alert_config['resource_alert_mode'] == 'specific':
                    # specific 模式：只显示指定天数内的资源
                    for region, region_resources in regional_resources.items():
                        filtered_regional_resources[region] = {}
                        for service_name, resources in region_resources.items():
                            if service_name in ['CVM', 'CBS', 'Lighthouse']:
                                filtered_regional_resources[region][service_name] = filter_resources_by_days(
                                    resources, 
                                    alert_config['resource_alert_days']
                                )
                            else:
                                filtered_regional_resources[region][service_name] = resources
                    
                    # 过滤全局资源
                    for service_name, resources in global_resources.items():
                        if service_name in ['Domain', 'SSL']:
                            filtered_global_resources[service_name] = filter_resources_by_days(
                                resources,
                                alert_config['resource_alert_days']
                            )
                        else:
                            filtered_global_resources[service_name] = resources
                else:
                    # all 模式：显示所有资源
                    filtered_regional_resources = regional_resources
                    filtered_global_resources = global_resources
                
                # 发送企业微信通知
                if alert_config['enable_wechat'] and wechat_service:
                    message = wechat_service.format_resource_message(
                        account_name, filtered_regional_resources, filtered_global_resources
                    )
                    
                    if message:  # 只有在有资源时才发送
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
                    
                    if content:  # 只有在有资源时才发送
                        if email_service.send_email(subject, content):
                            logger.info("[资源告警] 邮件通知发送成功")
                        else:
                            logger.error("[资源告警] 邮件通知发送失败")
            
            # 写入数据库（使用原始未过滤的资源）
            for region_data in regional_resources.values():
                if 'CVM' in region_data:
                    db_service.insert_cvm_instances(account_name, region_data['CVM'])
                if 'Lighthouse' in region_data:
                    db_service.insert_lighthouse_instances(account_name, region_data['Lighthouse'])
                if 'CBS' in region_data:
                    db_service.insert_cbs_disks(account_name, region_data['CBS'])

            if 'Domain' in global_resources:
                db_service.insert_domains(account_name, global_resources['Domain'])
            if 'SSL' in global_resources:
                db_service.insert_ssl_certificates(account_name, global_resources['SSL'])
        
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
    
    # 移到这里：所有账号处理完后再关闭连接
    db_service.close()

def display_results(account_name, regional_resources, global_resources):
    """按区域显示资源信息"""
    messages = [f"📢腾讯云 {account_name} 资源到期提醒\n"]
    
    # 处理CVM资源
    cvm_resources = []
    for region_data in regional_resources.values():
        if 'CVM' in region_data:
            cvm_resources.extend(region_data['CVM'])
    
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
    for region_data in regional_resources.values():
        if 'Lighthouse' in region_data:
            lighthouse_resources.extend(region_data['Lighthouse'])
    
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
    for region_data in regional_resources.values():
        if 'CBS' in region_data:
            cbs_resources.extend(region_data['CBS'])
    
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
    
    # 处理域名资源
    domain_resources = global_resources.get('Domain', [])
    if domain_resources:
        messages.append("=== 域名 ===")
        for resource in domain_resources:
            messages.extend([
                f"名称: {resource['Domain']}",
                f"到期时间: {resource['ExpiredTime']}",
                f"剩余天数: {resource['DifferDays']}天\n"
            ])
    
    # 处理SSL证书资源
    ssl_resources = global_resources.get('SSL', [])
    if ssl_resources:
        messages.append("=== SSL证书 ===")
        for resource in ssl_resources:
            messages.extend([
                f"域名: {resource['Domain']}",
                f"证书类型: {resource['ProductName']}",
                f"项目: {resource.get('ProjectName', '未知项目')}",
                f"到期时间: {resource['ExpiredTime']}",
                f"剩余天数: {resource['DifferDays']}天\n"
            ])
    
    print("\n".join(messages))

if __name__ == "__main__":
    main()
