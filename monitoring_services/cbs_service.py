import json
from .base_service import BaseService
from tencentcloud.cbs.v20170312 import cbs_client, models

class CBSService(BaseService):
    def init_client(self):
        """初始化CBS客户端"""
        self.client = cbs_client.CbsClient(self.cred, self.region, self.client_profile)

    def get_disks(self):
        """获取所有CBS云硬盘"""
        try:
            req = models.DescribeDisksRequest()
            resp = self.client.DescribeDisks(req)
            resp_dict = json.loads(resp.to_json_string())
            
            disks = []
            for disk in resp_dict.get("DiskSet", []):
                disks.append({
                    "Type": "CBS",
                    "DiskId": disk["DiskId"],
                    "DiskName": disk["DiskName"],
                    "ProjectId": disk["Placement"]["ProjectId"],
                    "ProjectName": disk["Placement"].get("ProjectName", "未知项目"),
                    "Zone": disk["Placement"]["Zone"],
                    "ExpiredTime": disk.get("DeadlineTime", ""),
                    "DifferDays": disk.get("DifferDaysOfDeadline"),
                    "Status": disk.get("DiskState", "Unknown")
                })
            
            return disks
            
        except Exception as e:
            print(f"获取CBS云硬盘信息时发生错误: {str(e)}")
            return [] 