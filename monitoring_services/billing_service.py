import json
from datetime import datetime
from tencentcloud.billing.v20180709 import billing_client, models
from .base_service import BaseService

class BillingService(BaseService):
    """账单服务类"""
    
    def init_client(self):
        """初始化账单客户端"""
        self.client = billing_client.BillingClient(self.cred, self.region, self.client_profile)
    
    def get_account_balance(self) -> float:
        """
        获取账号余额
        :return: 账号余额（元）
        """
        try:
            req = models.DescribeAccountBalanceRequest()
            resp = self.client.DescribeAccountBalance(req)
            return json.loads(resp.to_json_string())["RealBalance"] / 100  # 单位转换为元
        except Exception as e:
            print(f"获取账号余额时发生错误: {str(e)}")
            return 0.0
    
    def get_monthly_bill(self) -> dict:
        """
        获取月度账单信息
        :return: 账单详情字典
        """
        try:
            req = models.DescribeBillSummaryRequest()
            req.from_json_string(json.dumps({
                "Month": datetime.now().strftime("%Y-%m"),
                "GroupType": "project"
            }))
            resp = self.client.DescribeBillSummary(req)
            resp_dict = json.loads(resp.to_json_string())
            
            if "SummaryDetail" not in resp_dict:
                print("警告：响应中缺少 'SummaryDetail' 键")
                return {}
                
            bill_summary = resp_dict["SummaryDetail"]
            bill_details = {}
            
            # 处理每个项目的账单数据
            for project in bill_summary:
                project_name = project["GroupValue"] if project["GroupValue"] else "默认项目"
                bill_details[project_name] = {
                    "total": round(float(project["RealTotalCost"]), 2),
                    "services": {}
                }
                
                # 处理每个服务的详情
                if "Business" in project:
                    for business in project["Business"]:
                        service_name = business["BusinessCodeName"]
                        bill_details[project_name]["services"][service_name] = {
                            "RealTotalCost": round(float(business["RealTotalCost"]), 2),
                            "TotalCost": round(float(business["TotalCost"]), 2),
                            "CashPayAmount": round(float(business["CashPayAmount"]), 2)
                        }
            return bill_details
            
        except Exception as e:
            print(f"获取账单信息时发生错误: {str(e)}")
            return {}
            
    def format_bill_message(self, account_name: str, balance: float, bill_details: dict) -> str:
        """
        格式化账单信息为消息
        """
        messages = [
            f"腾讯云 {account_name} 账单信息\n",
            f"账号余额：{balance}元\n"
        ]
        
        if bill_details:
            messages.append("\n本月账单多维度汇总费用：")
            for project_name, details in bill_details.items():
                messages.append(f"\n项目名称：{project_name}")
                messages.append("服务详情：")
                for service_name, costs in details["services"].items():
                    messages.append(f"  - {service_name}: {costs['RealTotalCost']}元")
        
        return "\n".join(messages) 