import json
from .base_service import BaseService
from tencentcloud.cvm.v20170312 import cvm_client, models
from utils.time_utils import convert_utc_to_beijing, get_beijing_now
from typing import List, Dict
from .tag_service import TagService

class CVMService(BaseService):
    def init_client(self):
        """初始化CVM客户端"""
        self.client = cvm_client.CvmClient(self.cred, self.region, self.client_profile)
        self.tag_service = TagService(self.cred, self.region, self.client_profile)
    
    def get_instances(self) -> List[Dict]:
        """获取云服务器实例列表"""
        try:
            req = models.DescribeInstancesRequest()
            resp = self.client.DescribeInstances(req)
            
            instances = []
            if resp.InstanceSet:
                for instance in resp.InstanceSet:
                    # 获取项目名称
                    project_id = instance.Placement.ProjectId
                    project_name = self.tag_service.get_project_name(project_id) or "未知项目"
                    
                    # 计算剩余天数
                    expired_time = convert_utc_to_beijing(instance.ExpiredTime)
                    differ_days = (expired_time - get_beijing_now()).days
                    
                    instances.append({
                        'Type': 'CVM',
                        'InstanceId': instance.InstanceId,
                        'InstanceName': instance.InstanceName,
                        'Zone': instance.Placement.Zone,
                        'ProjectName': project_name,
                        'ExpiredTime': expired_time.strftime("%Y-%m-%d %H:%M:%S"),
                        'DifferDays': differ_days
                    })
            return instances
        except Exception as err:
            print(f"获取云服务器实例列表失败: {err}")
            return [] 