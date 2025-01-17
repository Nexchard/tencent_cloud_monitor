# 腾讯云资源到期监控

一个用于监控腾讯云资源到期时间和账单信息的工具，支持多账号管理和多种告警方式。

## 目录
- [功能特性](#功能特性)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [使用方法](#使用方法)
- [数据库支持](#数据库支持)
- [常见问题](#常见问题)

## 功能特性

### 资源监控
- CVM 云服务器
- Lighthouse 轻量应用服务器
- CBS 云硬盘
- 域名
- SSL证书

### 账单监控
- 账户余额查询
- 本月账单汇总
- 按项目统计费用

### 告警通知
- 企业微信机器人（支持多机器人）
- 云之家群组机器人（支持多机器人）
- 邮件通知
- 支持自定义告警规则

### 其他特性
- 多账号管理
- 多区域资源监控
- 数据库存储（可选）
- 模块化设计，易于扩展

## 环境要求

- Python 3.6+
- MySQL 5.7+（可选，用于数据存储）
- 腾讯云账号及 API 密钥

## 快速开始

1. 克隆项目
```bash
git clone https://github.com/Nexchard/tencent_cloud_monitor
cd tencent_cloud_monitor
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填写必要配置
```

4. 初始化数据库（可选）
```bash
python scripts/init_database.py
```

5. 运行程序
```bash
python main.py
```

## 配置说明

### 必要配置

1. 腾讯云账号配置（.env）
```env
# 账号配置（支持多账号）
ACCOUNT1_NAME=账号名称
ACCOUNT1_SECRET_ID=您的SecretId
ACCOUNT1_SECRET_KEY=您的SecretKey
```

2. 资源区域配置
```env
RESOURCE_SERVICE_REGIONS=ap-guangzhou,ap-shanghai
BILLING_SERVICE_REGION=ap-guangzhou
```

### 可选配置

1. 告警方式
```env
# 告警开关
ENABLE_WECHAT_ALERT=true
ENABLE_EMAIL_ALERT=true
ENABLE_YUNZHIJIA_ALERT=true

# 告警模式
RESOURCE_ALERT_MODE=specific  # all=全部告警, specific=指定天数告警
RESOURCE_ALERT_DAYS=65       # specific模式下的告警天数
```

2. 企业微信配置
```env
# 机器人配置
WECHAT_BOT1_NAME=机器人名称
WECHAT_BOT1_WEBHOOK=webhook地址

# 发送模式
WECHAT_SEND_MODE=specific    # all=发送给所有机器人, specific=指定机器人
WECHAT_TARGET_BOTS=机器人1,机器人2
```

3. 云之家配置
```env
# 机器人配置
YUNZHIJIA_BOT1_NAME=机器人名称
YUNZHIJIA_BOT1_WEBHOOK=webhook地址

# 发送模式
YUNZHIJIA_SEND_MODE=specific    # all=发送给所有机器人, specific=指定机器人
YUNZHIJIA_TARGET_BOTS=机器人1,机器人2
```

4. 邮件配置
```env
EMAIL_SMTP_SERVER=smtp.example.com
EMAIL_SMTP_PORT=465
EMAIL_SENDER=sender@example.com
EMAIL_PASSWORD=your_password
EMAIL_RECEIVERS=receiver1@example.com,receiver2@example.com
EMAIL_USE_SSL=true
```

5. 数据库配置
```env
ENABLE_DATABASE=true
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=your_database
DB_USER=your_username
DB_PASSWORD=your_password
```

## 使用方法

### 运行模式

1. 全部信息
```bash
python main.py --mode all
```

2. 仅资源信息
```bash
python main.py --mode resources
```

3. 仅账单信息
```bash
python main.py --mode billing
```

### 告警规则

- `all` 模式：显示所有资源信息
- `specific` 模式：仅显示指定天数内到期的资源
- 账单信息：不受天数限制，始终显示

## 数据库支持

### 初始化数据库
```bash
python scripts/init_database.py
```

### 数据表说明
- cvm_instances：云服务器信息
- cbs_disks：云硬盘信息
- lighthouse_instances：轻量应用服务器信息
- domains：域名信息
- ssl_certificates：SSL证书信息
- billing_info：账单信息

## 常见问题

### 1. API 密钥获取
- 访问腾讯云控制台
- 进入"访问管理" > "API密钥管理"
- 创建或查看密钥

### 2. 企业微信配置
- 在企业微信群中添加机器人
- 复制机器人的 Webhook 地址
- 填入配置文件

### 3. 云之家配置
- 在云之家群组中添加机器人
- 复制机器人的 Webhook 地址
- 填入配置文件

### 4. 邮件配置
- QQ邮箱需要使用授权码
- 需要开启 SMTP 服务
- 注意选择正确的端口号

## 许可证

MIT License 