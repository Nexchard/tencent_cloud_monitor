import json
from datetime import datetime
from .base_service import BaseService
from tencentcloud.ssl.v20191205 import ssl_client, models

class SSLService(BaseService):
    """SSL证书监控服务"""
    
    def init_client(self):
        """初始化SSL证书客户端"""
        self.client = ssl_client.SslClient(self.cred, self.region, self.client_profile)

    def get_certificates(self):
        """获取所有SSL证书"""
        try:
            req = models.DescribeCertificatesRequest()
            
            # 设置请求参数
            req.Limit = 100  # 每页返回的数量
            req.Offset = 0   # 偏移量，从0开始
            req.SearchKey = ""  # 搜索关键字
            req.CertificateType = "SVR"  # 证书类型：SVR = 服务器证书
            req.ExpirationSort = "DESC"  # 按过期时间降序排序
            
            # 发送请求并获取响应
            all_certificates = []
            while True:
                resp = self.client.DescribeCertificates(req)
                resp_dict = json.loads(resp.to_json_string())
                
                certificates = []
                for cert in resp_dict.get("Certificates", []):
                    # 只处理已颁发的证书
                    if cert.get("StatusName") == "证书已颁发":
                        # 计算剩余天数
                        expiration_date = datetime.strptime(cert["CertEndTime"], "%Y-%m-%d %H:%M:%S")
                        differ_days = (expiration_date - datetime.now()).days
                        
                        # 处理域名信息
                        domains = cert.get("CertSANs", []) or [cert["Domain"]]
                        domain_display = cert["Domain"]
                        if cert.get("IsWildcard"):
                            domain_display = f"{domain_display} (通配符证书)"
                        
                        certificates.append({
                            "Type": "SSL",
                            "CertificateId": cert["CertificateId"],
                            "Domain": domain_display,
                            "AllDomains": ", ".join(domains),
                            "ProjectId": cert.get("ProjectId"),
                            "ProjectName": cert.get("ProjectInfo", {}).get("ProjectName", "默认项目"),
                            "ExpiredTime": cert["CertEndTime"],
                            "DifferDays": differ_days,
                            "Status": cert["StatusName"],
                            "IsWildcard": cert.get("IsWildcard", False),
                            "ProductName": cert.get("ProductZhName", "未知类型")
                        })
                
                all_certificates.extend(certificates)
                
                # 检查是否还有更多数据
                total_count = resp_dict.get("Response", {}).get("TotalCount", 0)
                if req.Offset + req.Limit >= total_count:
                    break
                    
                # 更新偏移量获取下一页数据
                req.Offset += req.Limit
            
            return all_certificates
            
        except Exception as e:
            print(f"获取SSL证书信息时发生错误: {str(e)}")
            return [] 