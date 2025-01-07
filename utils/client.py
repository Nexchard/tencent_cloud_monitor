from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile

def get_client_profile():
    """创建客户端配置"""
    http_profile = HttpProfile()
    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile
    return client_profile

def create_credential(secret_id, secret_key):
    """创建认证信息"""
    return credential.Credential(secret_id, secret_key) 