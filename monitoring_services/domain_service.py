import json
from datetime import datetime
from .base_service import BaseService
from tencentcloud.domain.v20180808 import domain_client, models

class DomainService(BaseService):
    def init_client(self):
        """初始化域名服务客户端"""
        self.client = domain_client.DomainClient(self.cred, self.region, self.client_profile)

    def get_domains(self):
        """获取所有域名"""
        try:
            req = models.DescribeDomainNameListRequest()
            resp = self.client.DescribeDomainNameList(req)
            resp_dict = json.loads(resp.to_json_string())
            
            domains = []
            for domain in resp_dict.get("DomainSet", []):
                expiration_date = datetime.strptime(domain["ExpirationDate"], "%Y-%m-%d")
                differ_days = (expiration_date - datetime.now()).days

                domains.append({
                    "Type": "Domain",
                    "DomainId": domain["DomainId"],
                    "Domain": domain["DomainName"],
                    "ProjectId": None,
                    "ProjectName": None,
                    "Zone": None,
                    "ExpiredTime": domain["ExpirationDate"],
                    "DifferDays": differ_days,
                    "Status": domain.get("DomainStatus", "Unknown")
                })
            
            return domains
            
        except Exception as e:
            print(f"获取域名信息时发生错误: {str(e)}")
            return [] 