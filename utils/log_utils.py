import os
import logging
import pytz
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
import shutil

class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    """自定义日志处理器，支持自动清理旧日志"""
    
    def __init__(self, filename, when='D', interval=1, backup_count=365, 
                 encoding='utf-8', delay=False, utc=False, atTime=None):
        super().__init__(filename, when, interval, backup_count, 
                        encoding, delay, utc, atTime)
        self.clean_old_logs()
    
    def clean_old_logs(self):
        """清理一年前的日志文件"""
        try:
            log_dir = os.path.dirname(self.baseFilename)
            current_time = datetime.now()
            one_year_ago = current_time - timedelta(days=365)
            
            # 遍历日志目录
            for filename in os.listdir(log_dir):
                if not filename.endswith('.log'):
                    continue
                    
                file_path = os.path.join(log_dir, filename)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                # 删除超过一年的日志文件
                if file_mtime < one_year_ago:
                    os.remove(file_path)
                    print(f"已删除过期日志文件: {filename}")
        except Exception as e:
            print(f"清理日志文件失败: {str(e)}")

def setup_logger():
    """配置日志记录器"""
    # 创建logs目录
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 设置日志文件路径
    log_file = os.path.join(log_dir, 'tencent_cloud_monitor.log')
    
    # 创建日志记录器
    logger = logging.getLogger('TencentCloudMonitor')
    logger.setLevel(logging.INFO)
    
    # 创建格式化器（简化格式）
    file_formatter = logging.Formatter(
        '%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter('%(message)s')
    
    # 创建并配置文件处理器（每天轮换，保留一年的日志）
    file_handler = CustomTimedRotatingFileHandler(
        filename=log_file,
        when='midnight',
        interval=1,
        backup_count=365,
        encoding='utf-8'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)
    
    # 创建并配置控制台处理器（简化输出）
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    
    # 添加处理器到日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger 