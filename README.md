# 腾讯云资源到期监控

本项目用于监控腾讯云各类资源的到期时间和账单信息，支持多账号管理，并可通过企业微信机器人和邮件发送通知。

## 功能特性

- 支持监控的资源类型：
  - CVM 云服务器
  - Lighthouse 轻量应用服务器
  - CBS 云硬盘
  - 域名
- 支持查询账单信息：
  - 账户余额
  - 本月账单多维度汇总
- 告警通知支持：
  - 企业微信机器人（支持多机器人配置）
  - 邮件通知
- 其他特性：
  - 支持多账号监控
  - 自动转换时区为北京时间
  - 支持自定义告警配置
  - 模块化设计，易于扩展
  - 支持多区域资源监控

## 环境要求

- Python 3.6+
- 腾讯云账号及 API 密钥
- 企业微信机器人或邮箱配置（可选）

## 安装配置

1. 克隆项目到本地
2. 安装依赖包：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
复制 `.env.example` 文件为 `.env`，并填写以下配置：

### 账号配置
```env
# 账号1
ACCOUNT1_NAME=账号名称
ACCOUNT1_SECRET_ID=您的SecretId
ACCOUNT1_SECRET_KEY=您的SecretKey

# 账号2（如需配置多账号）
ACCOUNT2_NAME=账号名称
ACCOUNT2_SECRET_ID=您的SecretId
ACCOUNT2_SECRET_KEY=您的SecretKey
```

### 企业微信机器人配置
```env
# 企业微信机器人配置（支持多个）
WECHAT_BOT1_NAME=机器人名称
WECHAT_BOT1_WEBHOOK=机器人Webhook地址

WECHAT_BOT2_NAME=备用机器人
WECHAT_BOT2_WEBHOOK=备用机器人Webhook地址

# 发送配置
WECHAT_SEND_MODE=specific  # all=发送给所有机器人, specific=发送给指定机器人
WECHAT_TARGET_BOTS=机器人1,机器人2  # 指定接收消息的机器人名称，多个用逗号分隔
```

### 邮件配置
```env
EMAIL_SMTP_SERVER=smtp服务器地址
EMAIL_SMTP_PORT=端口号
EMAIL_SENDER=发件人邮箱
EMAIL_PASSWORD=邮箱密码或授权码
EMAIL_RECEIVERS=收件人1@example.com,收件人2@example.com
EMAIL_USE_SSL=true  # 是否启用SSL
```

### 告警方式配置
```env
ENABLE_EMAIL_ALERT=true    # 是否启用邮件告警
ENABLE_WECHAT_ALERT=true   # 是否启用企业微信告警
```

### 服务区域配置
```env
BILLING_SERVICE_REGION=ap-guangzhou  # 账单服务区域
RESOURCE_SERVICE_REGIONS=ap-guangzhou,ap-shanghai  # 资源服务区域，多个用逗号分隔
```

## 告警逻辑说明

1. 资源告警：
   - `all` 模式：所有资源信息都会触发告警
   - `specific` 模式：仅剩余天数小于等于 `RESOURCE_ALERT_DAYS` 的资源触发告警
   - 当没有满足条件的资源时，不会发送告警通知

2. 账单告警：
   - 不受资源告警天数限制
   - 只要启用了相应的告警方式就会发送

3. 终端显示：
   - 始终显示所有资源信息
   - 在 specific 模式下会显示告警资源的筛选结果

## 数据库支持

启用数据库后，系统会自动记录：
- 各类资源的详细信息
- 资源的到期时间和剩余天数
- 账单信息和费用明细
- 数据更新时间

## 使用方法

项目支持以下运行模式：

1. 查询所有信息：
```bash
python main.py --mode all
```

2. 仅查询资源信息：
```bash
python main.py --mode resources
```

3. 仅查询账单信息：
```bash
python main.py --mode billing
```

## 输出信息

程序运行后将输出以下信息：

1. 资源信息（按区域显示）：
   - CVM实例信息
   - CBS云硬盘信息
   - 域名信息

2. 账单信息：
   - 账户余额
   - 本月各项目的费用明细
   - 各服务的具体费用

## 通知内容

如果启用了通知功能，将通过配置的通知方式（企业微信/邮件）发送以下信息：

1. 账单通知：
   - 账户余额
   - 本月费用汇总
   - 各项目和服务的费用明细

2. 资源通知：
   - 各区域的资源列表
   - 资源到期时间
   - 即将到期的资源警告

## 常见问题

1. 如何获取腾讯云API密钥？
   - 登录腾讯云控制台
   - 进入"访问管理" > "API密钥管理"
   - 创建或查看SecretId和SecretKey

2. 如何获取企业微信机器人Webhook？
   - 在企业微信群中添加机器人
   - 获取机器人的Webhook地址

3. 邮箱配置说明：
   - 对于QQ邮箱，需要使用授权码而不是登录密码
   - 可以在邮箱设置中开启SMTP服务并获取授权码

## 注意事项

1. 请妥善保管API密钥等敏感信息
2. 建议定期检查和更新配置信息
3. 建议配置多种告警方式，确保消息送达
4. 数据库配置为可选项，不影响基本功能

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目。在提交代码前，请确保：

1. 代码符合项目的编码规范
2. 添加了必要的注释和文档
3. 测试通过并提供测试用例

## 许可证

MIT License 