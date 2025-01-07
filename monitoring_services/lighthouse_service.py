import json
from .base_service import BaseService
from tencentcloud.lighthouse.v20200324 import lighthouse_client, models
from utils.time_utils import convert_utc_to_beijing, get_beijing_now
from typing import List, Dict

class LighthouseService(BaseService):
    def init_client(self):
        """初始化Lighthouse客户端"""
        self.client = lighthouse_client.LighthouseClient(self.cred, self.region, self.client_profile)
    
    def get_instances(self) -> List[Dict]:
        """获取轻量应用服务器实例列表"""
        try:
            req = models.DescribeInstancesRequest()
            resp = self.client.DescribeInstances(req)
            
            instances = []
            if resp.InstanceSet:
                for instance in resp.InstanceSet:
                    # 计算剩余天数
                    expired_time = convert_utc_to_beijing(instance.ExpiredTime)
                    differ_days = (expired_time - get_beijing_now()).days
                    
                    instances.append({
                        'Type': 'Lighthouse',
                        'InstanceId': instance.InstanceId,
                        'InstanceName': instance.InstanceName,
                        'Zone': instance.Zone,
                        'ExpiredTime': expired_time.strftime("%Y-%m-%d %H:%M:%S"),
                        'DifferDays': differ_days
                    })
            return instances
        except Exception as err:
            print(f"获取轻量应用服务器实例列表失败: {err}")
            return [] 