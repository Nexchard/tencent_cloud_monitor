import requests
import logging
from typing import Dict, Optional, List

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
        
    def send_message(self, message: str, bot_names: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        发送企业微信消息
        :param message: 要发送的消息
        :param bot_names: 指定要发送的机器人名称列表，为None时发送给所有机器人
        :return: 发送结果字典 {bot_name: success}
        """
        results = {}
        target_bots = self.bots if bot_names is None else {
            name: self.bots[name] for name in bot_names if name in self.bots
        }
        
        for bot_name, bot_config in target_bots.items():
            try:
                data = {
                    "msgtype": "text",
                    "text": {"content": message}
                }
                response = requests.post(
                    url=bot_config["webhook_url"],
                    json=data,
                    timeout=5
                )
                response.raise_for_status()
                logger.info(f"消息发送成功 - 机器人[{bot_name}]: {response.status_code}")
                results[bot_name] = True
            except Exception as e:
                logger.error(f"发送消息失败 - 机器人[{bot_name}]: {str(e)}")
                results[bot_name] = False
                
        return results
            
    def format_resource_message(self, account_name, regional_resources, global_resources):
        """格式化资源信息为消息"""
        # 检查是否有需要告警的资源
        has_resources = False
        for resources in regional_resources.values():
            if resources:
                has_resources = True
                break
        for resources in global_resources.values():
            if resources:
                has_resources = True
                break
            
        if not has_resources:
            return ""  # 如果没有需要告警的资源，返回空字符串
        
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
        
        # 处理域名资源
        if global_resources.get('Domain'):
            messages.append("=== 域名 ===")
            for resource in global_resources['Domain']:
                messages.extend([
                    f"名称: {resource['Domain']}",
                    f"到期时间: {resource['ExpiredTime']}",
                    f"剩余天数: {resource['DifferDays']}天\n"
                ])
        
        return "\n".join(messages) 