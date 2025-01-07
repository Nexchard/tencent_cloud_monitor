class BaseService:
    """服务基类，处理通用逻辑"""
    DEFAULT_REGION = "ap-guangzhou"  # 默认region
    
    def __init__(self, cred, client_profile, region=None):
        self.cred = cred
        self.client_profile = client_profile
        self.region = region or self.DEFAULT_REGION
        self.init_client()
    
    def init_client(self):
        """初始化客户端，子类需要实现此方法"""
        raise NotImplementedError 