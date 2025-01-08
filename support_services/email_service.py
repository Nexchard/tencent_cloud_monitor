import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Union

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
        
    def send_email(self, subject: str, content: str) -> bool:
        """
        发送邮件
        :param subject: 邮件主题
        :param content: 邮件内容
        :return: 是否发送成功
        """
        try:
            # 创建邮件对象
            msg = MIMEMultipart()
            msg['From'] = self.sender
            msg['To'] = ','.join(self.receivers)
            msg['Subject'] = subject
            
            # 添加邮件正文
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # 连接SMTP服务器并发送
            if self.use_ssl:
                smtp = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                smtp = smtplib.SMTP(self.smtp_server, self.smtp_port)
                smtp.starttls()
            
            smtp.login(self.sender, self.password)
            smtp.send_message(msg)
            smtp.quit()
            
            logger.info("邮件发送成功")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {str(e)}")
            return False
            
    def format_resource_message(self, account_name, regional_resources, global_resources):
        """格式化资源信息为消息"""
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
        
        return "\n".join(messages) 