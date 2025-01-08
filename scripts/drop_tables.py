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
    'database': os.getenv('DB_DATABASE', 'tencent_cloud_monitor'),
    'port': int(os.getenv('DB_PORT', '3306'))
}

def drop_all_tables():
    """删除所有表"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        # 关闭外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # 删除每个表
        for (table_name,) in tables:
            print(f"删除表: {table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            
        # 恢复外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        conn.commit()
        print("所有表已删除！")
        
    except Exception as e:
        print(f"删除表时发生错误: {str(e)}")
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    drop_all_tables() 