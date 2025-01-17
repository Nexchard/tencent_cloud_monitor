import requests
import logging
from typing import Dict, List
import re

class YunZhiJiaService:
    """云之家机器人服务类"""
    
    def __init__(self, bots: Dict[str, Dict]):
        self.logger = logging.getLogger('TencentCloudMonitor')
        self.bots = bots
    
    def format_resource_message(self, account_name: str, regional_resources: Dict, global_resources: Dict) -> str:
        """
        格式化资源信息为文本消息
        """
        messages = [f"腾讯云 {account_name} 资源到期提醒\n"]
        
        # 处理CVM资源
        cvm_resources = []
        for region_data in regional_resources.values():
            if 'CVM' in region_data:
                cvm_resources.extend(region_data['CVM'])
        
        if cvm_resources:
            messages.append("===== 云服务器 =====")
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
            messages.append("===== 轻量应用服务器 =====")
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
            messages.append("===== 云硬盘 =====")
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
            messages.append("===== 域名 =====")
            for resource in domain_resources:
                messages.extend([
                    f"名称: {resource['Domain']}",
                    f"到期时间: {resource['ExpiredTime']}",
                    f"剩余天数: {resource['DifferDays']}天\n"
                ])
        
        # 处理SSL证书资源
        ssl_resources = global_resources.get('SSL', [])
        if ssl_resources:
            messages.append("===== SSL证书 =====")
            for resource in ssl_resources:
                messages.extend([
                    f"域名: {resource['Domain']}",
                    f"证书类型: {resource['ProductName']}",
                    f"项目: {resource.get('ProjectName', '未知项目')}",
                    f"到期时间: {resource['ExpiredTime']}",
                    f"剩余天数: {resource['DifferDays']}天\n"
                ])
        
        return "\n".join(messages)

    def format_billing_message(self, account_name: str, billing_info: Dict) -> str:
        """
        格式化账单信息为文本消息
        """
        messages = [f"腾讯云 {account_name} 账单信息\n"]
        
        messages.extend([
            "===== 账户余额 =====",
            f"当前余额: {billing_info['balance']}元\n",
            "===== 本月账单 ====="
        ])
        
        for project_name, details in billing_info['bill_details'].items():
            messages.append(f"\n项目: {project_name}")
            for service_name, costs in details["services"].items():
                messages.append(f"{service_name}: {costs['RealTotalCost']}元")
        
        return "\n".join(messages)

    def convert_markdown_to_text(self, markdown_text: str) -> str:
        """
        将markdown格式转换为纯文本格式
        """
        # 移除markdown特殊字符
        text = markdown_text
        text = re.sub(r'[#*`]', '', text)  # 移除#、*和`字符
        text = text.replace('📢', '')      # 移除表情符号
        
        # 统一分隔线样式
        text = text.replace('===', '=====')
        
        return text.strip()

    def send_message(self, message: str, bot_names: List[str] = None) -> Dict[str, bool]:
        """
        发送消息到云之家机器人
        :param message: 要发送的消息
        :param bot_names: 指定的机器人名称列表，如果为None则发送给所有机器人
        :return: 发送结果字典 {机器人名称: 是否成功}
        """
        results = {}
        target_bots = {name: self.bots[name] for name in (bot_names or self.bots.keys())}
        
        # 转换消息格式
        text_message = self.convert_markdown_to_text(message)
        
        for bot_name, bot_config in target_bots.items():
            try:
                # 打印请求信息
                self.logger.debug(f"正在发送消息到云之家机器人 {bot_name}")
                self.logger.debug(f"Webhook URL: {bot_config['webhook_url']}")
                self.logger.debug(f"请求内容: {text_message}")
                
                # 构造请求数据 - 修改为云之家要求的格式
                request_data = {
                    "content": text_message
                }
                self.logger.debug(f"请求数据: {request_data}")
                
                response = requests.post(
                    bot_config['webhook_url'],
                    json=request_data
                )
                
                # 打印响应信息
                self.logger.debug(f"响应状态码: {response.status_code}")
                self.logger.debug(f"响应内容: {response.text}")
                
                if response.status_code == 200:
                    resp_data = response.json()
                    self.logger.debug(f"响应JSON: {resp_data}")
                    
                    if resp_data.get('success') is True:  # 修改成功判断条件
                        self.logger.info(f"消息成功发送到云之家机器人 {bot_name}")
                        results[bot_name] = True
                    else:
                        error_msg = resp_data.get('error', '未知错误')
                        self.logger.error(f"发送消息到云之家机器人 {bot_name} 失败: {error_msg}")
                        self.logger.error(f"完整响应: {resp_data}")
                        results[bot_name] = False
                else:
                    self.logger.error(f"发送消息到云之家机器人 {bot_name} 失败: HTTP {response.status_code}")
                    self.logger.error(f"错误响应: {response.text}")
                    results[bot_name] = False
                    
            except Exception as e:
                self.logger.error(f"发送消息到云之家机器人 {bot_name} 时发生错误: {str(e)}")
                self.logger.exception("详细错误信息:")
                results[bot_name] = False
                
        return results 