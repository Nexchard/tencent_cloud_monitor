import mysql.connector
from typing import List, Dict
from datetime import datetime

class DatabaseService:
    def __init__(self, db_config):
        if not db_config.get('enable_db', False):
            self.enabled = False
            return
            
        self.enabled = True
        try:
            self.connection = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database'],
                port=int(db_config['port'])
            )
            self.cursor = self.connection.cursor()
        except Exception as e:
            print(f"数据库连接失败: {str(e)}")
            self.enabled = False

    def insert_cvm_instances(self, instances: List[Dict]):
        if not self.enabled:
            return
            
        for instance in instances:
            try:
                self.cursor.execute("""
                    INSERT INTO cvm_instances (instance_id, instance_name, zone, project_name, expired_time, differ_days, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    instance['InstanceId'],
                    instance['InstanceName'],
                    instance['Zone'],
                    instance['ProjectName'],
                    instance['ExpiredTime'],
                    instance['DifferDays'],
                    datetime.now()
                ))
                self.connection.commit()
            except Exception as e:
                print(f"插入CVM实例数据失败: {str(e)}")

    def insert_lighthouse_instances(self, instances: List[Dict]):
        if not self.enabled:
            return
            
        for instance in instances:
            try:
                self.cursor.execute("""
                    INSERT INTO lighthouse_instances (instance_id, instance_name, zone, expired_time, differ_days, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    instance['InstanceId'],
                    instance['InstanceName'],
                    instance['Zone'],
                    instance['ExpiredTime'],
                    instance['DifferDays'],
                    datetime.now()
                ))
                self.connection.commit()
            except Exception as e:
                print(f"插入轻量应用服务器实例数据失败: {str(e)}")

    def insert_cbs_disks(self, disks: List[Dict]):
        if not self.enabled:
            return
            
        for disk in disks:
            try:
                self.cursor.execute("""
                    INSERT INTO cbs_disks (disk_id, disk_name, project_id, project_name, zone, expired_time, differ_days, status, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    disk['DiskId'],
                    disk['DiskName'],
                    disk['ProjectId'],
                    disk['ProjectName'],
                    disk['Zone'],
                    disk['ExpiredTime'],
                    disk['DifferDays'],
                    disk['Status'],
                    datetime.now()
                ))
                self.connection.commit()
            except Exception as e:
                print(f"插入CBS云硬盘数据失败: {str(e)}")

    def insert_domains(self, domains: List[Dict]):
        if not self.enabled:
            return
            
        for domain in domains:
            try:
                self.cursor.execute("""
                    INSERT INTO domains (domain_id, domain_name, expired_time, differ_days, status, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    domain['DomainId'],
                    domain['Domain'],
                    domain['ExpiredTime'],
                    domain['DifferDays'],
                    domain['Status'],
                    datetime.now()
                ))
                self.connection.commit()
            except Exception as e:
                print(f"插入域名数据失败: {str(e)}")

    def insert_billing_info(self, account_name: str, balance: float, bill_details: Dict):
        if not self.enabled:
            return
            
        for project_name, details in bill_details.items():
            for service_name, costs in details["services"].items():
                try:
                    self.cursor.execute("""
                        INSERT INTO billing_info (account_name, balance, project_name, service_name, real_total_cost, total_cost, cash_pay_amount, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        account_name,
                        balance,
                        project_name,
                        service_name,
                        costs['RealTotalCost'],
                        costs['TotalCost'],
                        costs['CashPayAmount'],
                        datetime.now()
                    ))
                    self.connection.commit()
                except Exception as e:
                    print(f"插入账单数据失败: {str(e)}")

    def close(self):
        if self.enabled:
            self.cursor.close()
            self.connection.close() 