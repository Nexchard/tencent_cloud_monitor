import requests
import logging
from typing import Dict, Optional, List
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WeChatService:
    """企业微信服务类"""
    
    def __init__(self, bots_config: Dict[str, Dict]):
        """
        初始化企业微信服务
        :param bots_config: 机器人配置字典，格式为 {bot_name: {"webhook_url": url}}
        """
        self.bots = bots_config
        self.logger = logging.getLogger('TencentCloudMonitor')
        
    def send_message(self, message: str, bot_names: Optional[List[str]] = None) -> Dict[str, bool]:
        """发送企业微信消息"""
        results = {}
        target_bots = self.bots if bot_names is None else {
            name: self.bots[name] for name in bot_names if name in self.bots
        }
        
        for bot_name, bot_config in target_bots.items():
            try:
                data = {
                    "msgtype": "markdown",
                    "markdown": {"content": message}
                }
                response = requests.post(
                    url=bot_config["webhook_url"],
                    json=data,
                    timeout=5
                )
                response.raise_for_status()
                self.logger.info(f"消息发送成功 - 机器人[{bot_name}]")
                results[bot_name] = True
            except Exception as e:
                self.logger.error(f"发送消息失败 - 机器人[{bot_name}]: {str(e)}")
                results[bot_name] = False
                
        return results
            
    def format_resource_message(self, account_name, regional_resources, global_resources):
        """格式化资源信息为markdown消息"""
        messages = [
            f"## 📢 腾讯云资源到期提醒",
            f"### 账号：<font color='info'>{account_name}</font>\n"
        ]
        
        # 处理CVM资源
        cvm_resources = []
        for region_data in regional_resources.values():
            if 'CVM' in region_data:
                cvm_resources.extend(region_data['CVM'])
        
        if cvm_resources:
            messages.append("### 云服务器")
            for resource in cvm_resources:
                differ_days = resource['DifferDays']
                if differ_days <= 15:
                    days_color = "warning"  # 橙红色
                elif differ_days <= 30:
                    days_color = "info"     # 绿色
                else:
                    days_color = "comment"  # 灰色
                    
                resource_info = [
                    f"**名称**：{resource['InstanceName']}",
                    f"**项目**：{resource.get('ProjectName', '默认项目')}",
                    f"**区域**：{resource['Zone']}",
                    f"**到期时间**：{resource['ExpiredTime']}",
                    f"**剩余天数**：<font color='{days_color}'>{differ_days}天</font>"
                ]
                messages.append("> " + "\n> ".join(resource_info) + "\n")
        
        # 处理轻量应用服务器资源
        lighthouse_resources = []
        for region_data in regional_resources.values():
            if 'Lighthouse' in region_data:
                lighthouse_resources.extend(region_data['Lighthouse'])
        
        if lighthouse_resources:
            messages.append("### 轻量应用服务器")
            for resource in lighthouse_resources:
                differ_days = resource['DifferDays']
                if differ_days <= 15:
                    days_color = "warning"
                elif differ_days <= 30:
                    days_color = "info"
                else:
                    days_color = "comment"
                    
                resource_info = [
                    f"**名称**：{resource['InstanceName']}",
                    f"**区域**：{resource['Zone']}",
                    f"**到期时间**：{resource['ExpiredTime']}",
                    f"**剩余天数**：<font color='{days_color}'>{differ_days}天</font>"
                ]
                messages.append("> " + "\n> ".join(resource_info) + "\n")
        
        # 处理CBS资源
        cbs_resources = []
        for region_data in regional_resources.values():
            if 'CBS' in region_data:
                cbs_resources.extend(region_data['CBS'])
        
        if cbs_resources:
            messages.append("### 云硬盘")
            for resource in cbs_resources:
                differ_days = resource['DifferDays']
                if differ_days <= 15:
                    days_color = "warning"
                elif differ_days <= 30:
                    days_color = "info"
                else:
                    days_color = "comment"
                    
                resource_info = [
                    f"**名称**：{resource['DiskName']}",
                    f"**项目**：{resource['ProjectName']}",
                    f"**区域**：{resource['Zone']}",
                    f"**到期时间**：{resource['ExpiredTime']}",
                    f"**剩余天数**：<font color='{days_color}'>{differ_days}天</font>"
                ]
                messages.append("> " + "\n> ".join(resource_info) + "\n")
        
        # 处理域名资源
        domain_resources = global_resources.get('Domain', [])
        if domain_resources:
            messages.append("### 域名")
            for resource in domain_resources:
                differ_days = resource['DifferDays']
                if differ_days <= 15:
                    days_color = "warning"
                elif differ_days <= 30:
                    days_color = "info"
                else:
                    days_color = "comment"
                    
                resource_info = [
                    f"**名称**：{resource['Domain']}",
                    f"**到期时间**：{resource['ExpiredTime']}",
                    f"**剩余天数**：<font color='{days_color}'>{differ_days}天</font>"
                ]
                messages.append("> " + "\n> ".join(resource_info) + "\n")
        
        # 处理SSL证书资源
        ssl_resources = global_resources.get('SSL', [])
        if ssl_resources:
            messages.append("### SSL证书")
            for resource in ssl_resources:
                differ_days = resource['DifferDays']
                if differ_days <= 15:
                    days_color = "warning"
                elif differ_days <= 30:
                    days_color = "info"
                else:
                    days_color = "comment"
                    
                resource_info = [
                    f"**域名**：{resource['Domain']}",
                    f"**证书类型**：{resource['ProductName']}",
                    f"**项目**：{resource.get('ProjectName', '默认项目')}",
                    f"**到期时间**：{resource['ExpiredTime']}",
                    f"**剩余天数**：<font color='{days_color}'>{differ_days}天</font>"
                ]
                messages.append("> " + "\n> ".join(resource_info) + "\n")
        
        return "\n".join(messages) 