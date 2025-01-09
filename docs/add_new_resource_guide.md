# 新增告警资源操作指南

本指南详细说明如何在腾讯云资源到期监控系统中添加新的资源监控。

## 目录
- [1. 创建监控服务](#1-创建监控服务)
- [2. 创建数据库表](#2-创建数据库表)
- [3. 添加数据库服务方法](#3-添加数据库服务方法)
- [4. 更新告警消息格式化](#4-更新告警消息格式化)
- [5. 更新主程序](#5-更新主程序)
- [6. 更新文档](#6-更新文档)
- [7. 注意事项](#7-注意事项)

## 1. 创建监控服务

在 `monitoring_services` 目录下创建新的服务文件（例如：`new_service.py`）：

```python
from .base_service import BaseService
from tencentcloud.xxx.vXXX import xxx_client, models
from utils.time_utils import convert_utc_to_beijing, get_beijing_now

class NewService(BaseService):
    def init_client(self):
        """初始化客户端"""
        self.client = xxx_client.XxxClient(self.cred, self.region, self.client_profile)
    
    def get_resources(self) -> List[Dict]:
        """获取资源列表"""
        try:
            req = models.DescribeXxxRequest()
            resp = self.client.DescribeXxx(req)
            
            resources = []
            if resp.ResourceSet:
                for resource in resp.ResourceSet:
                    # 计算剩余天数
                    expired_time = convert_utc_to_beijing(resource.ExpiredTime)
                    differ_days = (expired_time - get_beijing_now()).days
                    
                    resources.append({
                        'Type': 'NewResource',
                        'ResourceId': resource.ResourceId,
                        'ResourceName': resource.ResourceName,
                        'ExpiredTime': expired_time.strftime("%Y-%m-%d %H:%M:%S"),
                        'DifferDays': differ_days
                    })
            return resources
        except Exception as err:
            print(f"获取资源列表失败: {err}")
            return []
```

## 2. 创建数据库表

在 `sql` 目录下创建新的 SQL 文件（例如：`new_service.sql`）：

```sql
CREATE TABLE IF NOT EXISTS new_resources (
    id SERIAL PRIMARY KEY,
    account_name VARCHAR(255),
    resource_id VARCHAR(255) NOT NULL,
    resource_name VARCHAR(255),
    expired_time TIMESTAMP,
    differ_days INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 3. 添加数据库服务方法

在 `support_services/database_service.py` 中添加新方法：

```python
def insert_new_resources(self, account_name: str, resources: List[Dict]):
    if not self.enabled or not self.ensure_connection():
        return
            
    success_count = 0
    for resource in resources:
        try:
            self.cursor.execute("""
                INSERT INTO new_resources 
                (account_name, resource_id, resource_name, expired_time, differ_days, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                resource_name = VALUES(resource_name),
                expired_time = VALUES(expired_time),
                differ_days = VALUES(differ_days),
                updated_at = VALUES(updated_at)
            """, (
                account_name,
                resource['ResourceId'],
                resource['ResourceName'],
                resource['ExpiredTime'],
                resource['DifferDays'],
                datetime.now()
            ))
            self.connection.commit()
            success_count += 1
        except Exception as e:
            self.logger.error(f"插入新资源数据失败: {str(e)}")
    
    self.logger.info(f"新资源数据写入完成: 成功 {success_count}/{len(resources)}")
```

## 4. 更新告警消息格式化

在 `support_services/wechat_service.py` 和 `support_services/email_service.py` 中的 `format_resource_message` 方法中添加新资源处理：

```python
def format_resource_message(self, account_name, regional_resources, global_resources):
    messages = [f"📢腾讯云 {account_name} 资源到期提醒\n"]
    
    # ... 其他资源的处理 ...
    
    # 处理新资源
    new_resources = []
    for region_data in regional_resources.values():
        if 'NewResource' in region_data:
            new_resources.extend(region_data['NewResource'])
    
    if new_resources:
        messages.append("=== 新资源 ===")
        for resource in new_resources:
            messages.extend([
                f"名称: {resource['ResourceName']}",
                f"到期时间: {resource['ExpiredTime']}",
                f"剩余天数: {resource['DifferDays']}天\n"
            ])
```

## 5. 更新主程序

在 `main.py` 中的 `SERVICE_TYPES` 字典中添加新服务：

```python
SERVICE_TYPES = {
    'RESOURCE_SERVICES': {
        'REGIONAL': {
            # ... 其他服务 ...
            'NewResource': {
                'regions': None,  # 将在运行时从配置加载
                'service_class': NewService
            }
        }
    }
}
```

## 6. 更新文档

在 `README.md` 中的资源监控列表中添加新资源说明。

## 7. 注意事项

1. 数据结构规范
   - 所有资源必须包含以下字段：
     - Type: 资源类型标识
     - ResourceId: 资源唯一标识
     - ResourceName: 资源名称
     - ExpiredTime: 到期时间
     - DifferDays: 剩余天数

2. 区域资源 vs 全局资源
   - 区域资源：需要在 `REGIONAL` 中定义
   - 全局资源：需要在 `GLOBAL` 中定义

3. 数据库操作
   - 确保表名和字段名遵循现有命名规范
   - 使用 `ON DUPLICATE KEY UPDATE` 处理重复数据

4. 告警处理
   - 确保正确实现资源过滤逻辑
   - 保持消息格式的一致性

5. 测试清单
   - [ ] 资源获取功能
   - [ ] 数据库写入
   - [ ] 告警过滤
   - [ ] 消息格式化
   - [ ] 企业微信通知
   - [ ] 邮件通知

## 示例代码结构

```
monitoring_services/
  └── new_service.py         # 新资源监控服务
sql/
  └── new_service.sql        # 数据库表定义
``` 