import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Dict, Union
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmailService:
    """邮件服务类"""
    
    def __init__(self, config: Dict[str, Union[str, List[str], bool]]):
        """
        初始化邮件服务
        :param config: 邮件配置字典
        """
        self.smtp_server = config['smtp_server']
        self.smtp_port = config['smtp_port']
        self.sender = config['sender']
        self.password = config['password']
        self.receivers = config['receivers']
        self.use_ssl = config['use_ssl']
        self.logger = logging.getLogger('TencentCloudMonitor')
        
    def send_email(self, subject: str, content: str) -> bool:
        """发送带HTML附件的邮件"""
        try:
            msg = MIMEMultipart('alternative')  # 使用 alternative 类型
            msg['From'] = self.sender
            msg['To'] = ','.join(self.receivers)
            msg['Subject'] = subject
            
            # 添加HTML正文
            html_part = MIMEText(content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 生成HTML附件
            html_filename = f"腾讯云资源报告-{datetime.now().strftime('%Y%m%d')}.html"
            html_attachment = MIMEApplication(content.encode('utf-8'), _subtype="html")
            html_attachment.add_header('Content-Disposition', 'attachment', 
                                     filename=html_filename)
            msg.attach(html_attachment)
            
            # 发送邮件
            if self.use_ssl:
                smtp = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                smtp = smtplib.SMTP(self.smtp_server, self.smtp_port)
                smtp.starttls()
            
            smtp.login(self.sender, self.password)
            smtp.send_message(msg)
            smtp.quit()
            
            self.logger.info("邮件发送成功")
            return True
            
        except Exception as e:
            self.logger.error(f"邮件发送失败: {str(e)}")
            return False
            
    def format_resource_message(self, account_name, regional_resources, global_resources):
        """格式化资源信息为HTML消息"""
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1 {{
                    color: #1a73e8;
                    border-bottom: 2px solid #1a73e8;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #202124;
                    margin-top: 30px;
                }}
                h3 {{
                    color: #1a73e8;
                    margin-top: 20px;
                }}
                .account {{
                    background: #f8f9fa;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .service {{
                    margin-bottom: 20px;
                }}
                .resource {{
                    background: white;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 6px;
                    border-left: 4px solid #1a73e8;
                }}
                .resource p {{
                    margin: 5px 0;
                }}
                .warning {{
                    border-left: 4px solid #f44336;
                }}
                .warning .days {{
                    color: #f44336;
                    font-weight: bold;
                }}
                .medium .days {{
                    color: #fb8c00;
                    font-weight: bold;
                }}
                .normal .days {{
                    color: #1a73e8;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <h1>📢 腾讯云资源到期提醒</h1>
            <div class='account'>
                <h2>账号：{account_name}</h2>
        """

        # 处理CVM资源
        cvm_resources = []
        for region_data in regional_resources.values():
            if 'CVM' in region_data:
                cvm_resources.extend(region_data['CVM'])
        
        if cvm_resources:
            html += "<div class='service'>"
            html += "<h3>云服务器</h3>"
            for resource in cvm_resources:
                differ_days = resource['DifferDays']
                if differ_days <= 15:
                    resource_class = "warning"
                elif differ_days <= 30:
                    resource_class = "medium"
                else:
                    resource_class = "normal"
                    
                html += f"""
                <div class='resource {resource_class}'>
                    <p><strong>名称：</strong>{resource['InstanceName']}</p>
                    <p><strong>项目：</strong>{resource.get('ProjectName', '默认项目')}</p>
                    <p><strong>区域：</strong>{resource['Zone']}</p>
                    <p><strong>到期时间：</strong>{resource['ExpiredTime']}</p>
                    <p><strong>剩余天数：</strong><span class='days'>{differ_days}天</span></p>
                </div>
                """
            html += "</div>"
        
        # 处理轻量应用服务器资源
        lighthouse_resources = []
        for region_data in regional_resources.values():
            if 'Lighthouse' in region_data:
                lighthouse_resources.extend(region_data['Lighthouse'])
        
        if lighthouse_resources:
            html += "<div class='service'>"
            html += "<h3>轻量应用服务器</h3>"
            for resource in lighthouse_resources:
                differ_days = resource['DifferDays']
                if differ_days <= 15:
                    resource_class = "warning"
                elif differ_days <= 30:
                    resource_class = "medium"
                else:
                    resource_class = "normal"
                    
                html += f"""
                <div class='resource {resource_class}'>
                    <p><strong>名称：</strong>{resource['InstanceName']}</p>
                    <p><strong>区域：</strong>{resource['Zone']}</p>
                    <p><strong>到期时间：</strong>{resource['ExpiredTime']}</p>
                    <p><strong>剩余天数：</strong><span class='days'>{differ_days}天</span></p>
                </div>
                """
            html += "</div>"
        
        # 处理CBS资源
        cbs_resources = []
        for region_data in regional_resources.values():
            if 'CBS' in region_data:
                cbs_resources.extend(region_data['CBS'])
        
        if cbs_resources:
            html += "<div class='service'>"
            html += "<h3>云硬盘</h3>"
            for resource in cbs_resources:
                differ_days = resource['DifferDays']
                if differ_days <= 15:
                    resource_class = "warning"
                elif differ_days <= 30:
                    resource_class = "medium"
                else:
                    resource_class = "normal"
                    
                html += f"""
                <div class='resource {resource_class}'>
                    <p><strong>名称：</strong>{resource['DiskName']}</p>
                    <p><strong>项目：</strong>{resource['ProjectName']}</p>
                    <p><strong>区域：</strong>{resource['Zone']}</p>
                    <p><strong>到期时间：</strong>{resource['ExpiredTime']}</p>
                    <p><strong>剩余天数：</strong><span class='days'>{differ_days}天</span></p>
                </div>
                """
            html += "</div>"
        
        # 处理域名资源
        domain_resources = global_resources.get('Domain', [])
        if domain_resources:
            html += "<div class='service'>"
            html += "<h3>域名</h3>"
            for resource in domain_resources:
                differ_days = resource['DifferDays']
                if differ_days <= 15:
                    resource_class = "warning"
                elif differ_days <= 30:
                    resource_class = "medium"
                else:
                    resource_class = "normal"
                    
                html += f"""
                <div class='resource {resource_class}'>
                    <p><strong>名称：</strong>{resource['Domain']}</p>
                    <p><strong>到期时间：</strong>{resource['ExpiredTime']}</p>
                    <p><strong>剩余天数：</strong><span class='days'>{differ_days}天</span></p>
                </div>
                """
            html += "</div>"
        
        # 处理SSL证书资源
        ssl_resources = global_resources.get('SSL', [])
        if ssl_resources:
            html += "<div class='service'>"
            html += "<h3>SSL证书</h3>"
            for resource in ssl_resources:
                differ_days = resource['DifferDays']
                if differ_days <= 15:
                    resource_class = "warning"
                elif differ_days <= 30:
                    resource_class = "medium"
                else:
                    resource_class = "normal"
                    
                html += f"""
                <div class='resource {resource_class}'>
                    <p><strong>域名：</strong>{resource['Domain']}</p>
                    <p><strong>证书类型：</strong>{resource['ProductName']}</p>
                    <p><strong>项目：</strong>{resource.get('ProjectName', '默认项目')}</p>
                    <p><strong>到期时间：</strong>{resource['ExpiredTime']}</p>
                    <p><strong>剩余天数：</strong><span class='days'>{differ_days}天</span></p>
                </div>
                """
            html += "</div>"
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html 

    def format_summary_message(self, all_accounts_data):
        """格式化所有账号的资源和账单信息为HTML消息"""
        html = self._get_html_header()
        html += self._format_balance_summary(all_accounts_data)
        
        for account_data in all_accounts_data:
            html += self._format_account_info(account_data)
        
        html += "</body></html>"
        return html

    def _get_html_header(self):
        """生成HTML头部和样式"""
        return """
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 10px; }
        h2 { color: #202124; margin-top: 30px; }
        h3 { color: #1a73e8; margin-top: 20px; }
        .account { background: #f8f9fa; border-radius: 8px; padding: 20px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .service { margin-bottom: 20px; }
        .resource { background: white; padding: 15px; margin: 10px 0; border-radius: 6px; border-left: 4px solid #1a73e8; }
        .resource p { margin: 5px 0; }
        .warning { border-left: 4px solid #f44336; }
        .warning .days { color: #f44336; font-weight: bold; }
        .medium .days { color: #fb8c00; font-weight: bold; }
        .normal .days { color: #1a73e8; font-weight: bold; }
        .billing-info { background: #e8f0fe; padding: 15px; border-radius: 6px; margin: 20px 0; }
        .billing-info h3 { margin-top: 0; color: #1a73e8; }
        .balance { font-size: 1.2em; color: #1a73e8; font-weight: bold; }
        .bill-item { background: white; padding: 10px 15px; margin: 5px 0; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>📢 腾讯云资源和账单汇总报告</h1>
"""

    def _format_balance_summary(self, all_accounts_data):
        """格式化余额汇总信息"""
        html = "<div class='billing-info'><h3>账户余额汇总</h3>"
        for account_data in all_accounts_data:
            account_name = account_data['account_name']
            billing_info = account_data.get('billing')
            if billing_info:
                html += f"<p><strong>账号：{account_name}</strong> - <span class='balance'>{billing_info['balance']} 元</span></p>"
        html += "</div>"
        return html

    def _format_account_info(self, account_data):
        """格式化单个账号的信息"""
        account_name = account_data['account_name']
        resources = account_data['resources']
        regional_resources = resources.get('regional', {})
        global_resources = resources.get('global', {})
        
        html = f"<div class='account'><h2>账号：{account_name}</h2>"
        
        if account_data.get('billing'):
            html += self._format_billing_info(account_data['billing'])
        
        html += self._format_resources(regional_resources, global_resources)
        html += "</div>"
        return html

    def _format_billing_info(self, billing_info):
        """格式化账单信息"""
        html = "<div class='service'><h3>本月账单</h3>"
        for project_name, details in billing_info['bill_details'].items():
            html += "<div class='bill-item'>"
            html += f"<p><strong>项目：{project_name}</strong></p>"
            for service_name, costs in details['services'].items():
                html += f"<p>{service_name}: {costs['RealTotalCost']}元</p>"
            html += "</div>"
        html += "</div>"
        return html

    def _format_resources(self, regional_resources, global_resources):
        """格式化资源信息"""
        html = ""
        
        # 处理区域资源
        resource_types = {
            'CVM': {'name': '云服务器', 'key': 'InstanceName'},
            'Lighthouse': {'name': '轻量应用服务器', 'key': 'InstanceName'},
            'CBS': {'name': '云硬盘', 'key': 'DiskName'}
        }
        
        for service_type, config in resource_types.items():
            resources = []
            for region_data in regional_resources.values():
                if service_type in region_data:
                    resources.extend(region_data[service_type])
            
            # 只有在有资源时才添加这个区块
            if resources:
                html += self._format_resource_section(
                    config['name'], 
                    resources, 
                    config['key']
                )
        
        # 处理全局资源
        if 'Domain' in global_resources and global_resources['Domain']:  # 只在有域名时显示
            html += self._format_resource_section(
                '域名',
                global_resources['Domain'],
                'Domain'
            )
        
        if 'SSL' in global_resources and global_resources['SSL']:  # 只在有SSL证书时显示
            html += self._format_ssl_section(global_resources['SSL'])
        
        return html

    def _format_resource_section(self, title, resources, name_key):
        """格式化资源区块"""
        html = f"<div class='service'><h3>{title}</h3>"
        for resource in resources:
            differ_days = resource['DifferDays']
            resource_class = self._get_resource_class(differ_days)
            
            html += f"<div class='resource {resource_class}'>"
            html += f"<p><strong>名称：</strong>{resource[name_key]}</p>"
            
            if 'ProjectName' in resource:
                html += f"<p><strong>项目：</strong>{resource['ProjectName']}</p>"
            if 'Zone' in resource:
                html += f"<p><strong>区域：</strong>{resource['Zone']}</p>"
                
            html += f"<p><strong>到期时间：</strong>{resource['ExpiredTime']}</p>"
            html += f"<p><strong>剩余天数：</strong><span class='days'>{differ_days}天</span></p>"
            html += "</div>"
        html += "</div>"
        return html

    def _format_ssl_section(self, ssl_resources):
        """格式化SSL证书区块"""
        html = "<div class='service'><h3>SSL证书</h3>"
        for resource in ssl_resources:
            differ_days = resource['DifferDays']
            resource_class = self._get_resource_class(differ_days)
            
            html += f"<div class='resource {resource_class}'>"
            html += f"<p><strong>域名：</strong>{resource['Domain']}</p>"
            html += f"<p><strong>证书类型：</strong>{resource['ProductName']}</p>"
            html += f"<p><strong>项目：</strong>{resource.get('ProjectName', '默认项目')}</p>"
            html += f"<p><strong>到期时间：</strong>{resource['ExpiredTime']}</p>"
            html += f"<p><strong>剩余天数：</strong><span class='days'>{differ_days}天</span></p>"
            html += "</div>"
        html += "</div>"
        return html

    def _get_resource_class(self, differ_days):
        """根据剩余天数获取样式类名"""
        if differ_days <= 15:
            return "warning"
        elif differ_days <= 30:
            return "medium"
        return "normal" 