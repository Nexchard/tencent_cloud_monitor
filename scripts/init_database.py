import os
import mysql.connector
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': int(os.getenv('DB_PORT', '3306'))
}

def create_database():
    """创建数据库"""
    try:
        # 连接MySQL（不指定数据库）
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # 创建数据库
        database_name = os.getenv('DB_DATABASE', 'tencent_cloud_monitor')
        print(f"创建数据库 {database_name}...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"数据库 {database_name} 创建成功！")
        
        # 切换到新创建的数据库
        cursor.execute(f"USE {database_name}")
        
        # SQL文件目录
        sql_dir = 'sql'
        
        # SQL文件列表
        sql_files = [
            'cvm_service.sql',
            'cbs_service.sql',
            'lighthouse_service.sql',
            'domain_service.sql',
            'ssl_service.sql',
            'billing_service.sql'
        ]
        
        # 执行每个SQL文件
        for sql_file in sql_files:
            file_path = os.path.join(sql_dir, sql_file)
            print(f"执行 {sql_file}...")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    sql = f.read()
                    cursor.execute(sql)
            except FileNotFoundError:
                print(f"警告: 找不到文件 {file_path}")
                continue
            except Exception as e:
                print(f"执行 {sql_file} 时发生错误: {str(e)}")
                raise
        
        # 提交更改
        conn.commit()
        print("数据库初始化完成！")
        
    except Exception as e:
        print(f"初始化数据库时发生错误: {str(e)}")
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_database() 