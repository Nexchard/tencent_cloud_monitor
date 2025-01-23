import mysql.connector
from typing import List, Dict
from datetime import datetime
import logging
import uuid

class DatabaseService:
    def __init__(self, db_config):
        self.logger = logging.getLogger('TencentCloudMonitor')
        
        if not db_config.get('enable_db', False):
            self.logger.info("数据库功能未启用 (ENABLE_DATABASE=false)")
            self.enabled = False
            return
            
        self.db_config = db_config
        self.enabled = True
        self.current_batch = self._generate_batch_number()
        try:
            self.connection = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database'],
                port=int(db_config['port'])
            )
            self.cursor = self.connection.cursor()
            self.logger.info(f"成功连接到数据库 {db_config['database']}")
        except Exception as e:
            self.logger.error(f"数据库连接失败: {str(e)}")
            self.enabled = False

    def _generate_batch_number(self) -> str:
        """生成批次号，使用时间戳格式：YYYYMMDDHHMMSS"""
        return datetime.now().strftime('%Y%m%d%H%M%S')

    def insert_cvm_instances(self, account_name: str, instances: List[Dict]):
        if not self.enabled or not self.ensure_connection():
            return
            
        success_count = 0
        for instance in instances:
            try:
                self.cursor.execute("""
                    INSERT INTO cvm_instances 
                    (account_name, instance_id, instance_name, zone, project_name, expired_time, differ_days, batch_number, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    instance_name = VALUES(instance_name),
                    zone = VALUES(zone),
                    project_name = VALUES(project_name),
                    expired_time = VALUES(expired_time),
                    differ_days = VALUES(differ_days),
                    batch_number = VALUES(batch_number),
                    updated_at = VALUES(updated_at)
                """, (
                    account_name,
                    instance['InstanceId'],
                    instance['InstanceName'],
                    instance['Zone'],
                    instance.get('ProjectName', '默认项目'),
                    instance['ExpiredTime'],
                    instance['DifferDays'],
                    self.current_batch,
                    datetime.now()
                ))
                self.connection.commit()
                success_count += 1
            except Exception as e:
                self.logger.error(f"插入CVM实例数据失败 - {instance.get('InstanceName', 'unknown')}: {str(e)}")
        
        if instances:
            self.logger.info(f"CVM实例数据写入完成: 成功 {success_count}/{len(instances)}")

    def insert_lighthouse_instances(self, account_name: str, instances: List[Dict]):
        if not self.enabled or not self.ensure_connection():
            return
            
        success_count = 0
        for instance in instances:
            try:
                self.cursor.execute("""
                    INSERT INTO lighthouse_instances 
                    (account_name, instance_id, instance_name, zone, expired_time, differ_days, batch_number, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    instance_name = VALUES(instance_name),
                    zone = VALUES(zone),
                    expired_time = VALUES(expired_time),
                    differ_days = VALUES(differ_days),
                    batch_number = VALUES(batch_number),
                    updated_at = VALUES(updated_at)
                """, (
                    account_name,
                    instance['InstanceId'],
                    instance['InstanceName'],
                    instance['Zone'],
                    instance['ExpiredTime'],
                    instance['DifferDays'],
                    self.current_batch,
                    datetime.now()
                ))
                self.connection.commit()
                success_count += 1
            except Exception as e:
                self.logger.error(f"插入轻量应用服务器实例数据失败 - {instance.get('InstanceName', 'unknown')}: {str(e)}")
        
        if instances:
            self.logger.info(f"轻量应用服务器实例数据写入完成: 成功 {success_count}/{len(instances)}")

    def insert_cbs_disks(self, account_name: str, disks: List[Dict]):
        if not self.enabled or not self.ensure_connection():
            return
            
        success_count = 0
        for disk in disks:
            try:
                self.cursor.execute("""
                    INSERT INTO cbs_disks 
                    (account_name, disk_id, disk_name, project_name, zone, expired_time, differ_days, batch_number, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    disk_name = VALUES(disk_name),
                    project_name = VALUES(project_name),
                    zone = VALUES(zone),
                    expired_time = VALUES(expired_time),
                    differ_days = VALUES(differ_days),
                    batch_number = VALUES(batch_number),
                    updated_at = VALUES(updated_at)
                """, (
                    account_name,
                    disk['DiskId'],
                    disk['DiskName'],
                    disk.get('ProjectName', '默认项目'),
                    disk['Zone'],
                    disk['ExpiredTime'],
                    disk['DifferDays'],
                    self.current_batch,
                    datetime.now()
                ))
                self.connection.commit()
                success_count += 1
            except Exception as e:
                self.logger.error(f"插入云硬盘数据失败 - {disk.get('DiskName', 'unknown')}: {str(e)}")
        
        if disks:
            self.logger.info(f"云硬盘数据写入完成: 成功 {success_count}/{len(disks)}")

    def insert_domains(self, account_name: str, domains: List[Dict]):
        if not self.enabled or not self.ensure_connection():
            return
            
        success_count = 0
        for domain in domains:
            try:
                self.cursor.execute("""
                    INSERT INTO domains 
                    (account_name, domain_id, domain_name, expired_time, differ_days, batch_number, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    domain_name = VALUES(domain_name),
                    expired_time = VALUES(expired_time),
                    differ_days = VALUES(differ_days),
                    batch_number = VALUES(batch_number),
                    updated_at = VALUES(updated_at)
                """, (
                    account_name,
                    domain['DomainId'],
                    domain['Domain'],
                    domain['ExpiredTime'],
                    domain['DifferDays'],
                    self.current_batch,
                    datetime.now()
                ))
                self.connection.commit()
                success_count += 1
            except Exception as e:
                self.logger.error(f"插入域名数据失败 - {domain.get('Domain', 'unknown')}: {str(e)}")
        
        if domains:
            self.logger.info(f"域名数据写入完成: 成功 {success_count}/{len(domains)}")

    def insert_billing_info(self, account_name: str, balance: float, bill_details: Dict):
        """插入账单数据"""
        if not self.enabled or not self.ensure_connection():
            self.logger.warning("数据库未启用或连接失败，跳过账单数据写入")
            return
            
        total_count = 1  # 余额记录
        success_count = 0
        
        try:
            # 插入余额记录
            self.logger.debug(f"正在写入账户 {account_name} 的余额信息: {balance}")
            self.cursor.execute("""
                INSERT INTO billing_info 
                (account_name, project_name, service_name, balance, real_total_cost, total_cost, cash_pay_amount, batch_number, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                balance = VALUES(balance),
                real_total_cost = VALUES(real_total_cost),
                total_cost = VALUES(total_cost),
                cash_pay_amount = VALUES(cash_pay_amount),
                batch_number = VALUES(batch_number),
                updated_at = VALUES(updated_at)
            """, (
                account_name,
                '系统',
                '账户余额',
                balance,
                0,
                0,
                0,
                self.current_batch,
                datetime.now()
            ))
            self.connection.commit()
            success_count += 1
            self.logger.debug("余额信息写入成功")
        except Exception as e:
            self.logger.error(f"插入账户余额数据失败: {str(e)}")
        
        # 计算总服务数
        for project_name, details in bill_details.items():
            total_count += len(details["services"])
        
        # 插入服务费用记录
        for project_name, details in bill_details.items():
            for service_name, costs in details["services"].items():
                try:
                    self.logger.debug(f"正在写入项目 {project_name} 服务 {service_name} 的账单信息")
                    self.cursor.execute("""
                        INSERT INTO billing_info 
                        (account_name, project_name, service_name, balance, real_total_cost, total_cost, cash_pay_amount, batch_number, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        balance = VALUES(balance),
                        real_total_cost = VALUES(real_total_cost),
                        total_cost = VALUES(total_cost),
                        cash_pay_amount = VALUES(cash_pay_amount),
                        batch_number = VALUES(batch_number),
                        updated_at = VALUES(updated_at)
                    """, (
                        account_name,
                        project_name,
                        service_name,
                        0,
                        costs['RealTotalCost'],
                        costs['TotalCost'],
                        costs['CashPayAmount'],
                        self.current_batch,
                        datetime.now()
                    ))
                    self.connection.commit()
                    success_count += 1
                except Exception as e:
                    self.logger.error(f"插入账单数据失败 - 项目: {project_name}, 服务: {service_name}: {str(e)}")
        
        self.logger.info(f"账单数据写入完成: 成功 {success_count}/{total_count}")

    def insert_ssl_certificates(self, account_name: str, certificates: List[Dict]):
        """插入SSL证书数据"""
        if not self.enabled or not self.ensure_connection():
            return
            
        success_count = 0
        for cert in certificates:
            try:
                self.cursor.execute("""
                    INSERT INTO ssl_certificates 
                    (account_name, certificate_id, domain, product_name, project_name, 
                    expired_time, differ_days, batch_number, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    domain = VALUES(domain),
                    product_name = VALUES(product_name),
                    project_name = VALUES(project_name),
                    expired_time = VALUES(expired_time),
                    differ_days = VALUES(differ_days),
                    batch_number = VALUES(batch_number),
                    updated_at = VALUES(updated_at)
                """, (
                    account_name,
                    cert['CertificateId'],
                    cert['Domain'],
                    cert['ProductName'],
                    cert['ProjectName'],
                    cert['ExpiredTime'],
                    cert['DifferDays'],
                    self.current_batch,
                    datetime.now()
                ))
                self.connection.commit()
                success_count += 1
            except Exception as e:
                self.logger.error(f"插入SSL证书数据失败 - {cert.get('Domain', 'unknown')}: {str(e)}")
        
        if certificates:
            self.logger.info(f"SSL证书数据写入完成: 成功 {success_count}/{len(certificates)}")

    def close(self):
        """关闭数据库连接"""
        if self.enabled:
            try:
                while self.connection.unread_result:
                    self.cursor.fetchall()
                self.cursor.close()
                self.connection.close()
                self.logger.info("数据库连接已关闭")
            except Exception as e:
                self.logger.error(f"关闭数据库连接时发生错误: {str(e)}")

    def ensure_connection(self):
        """确保数据库连接有效"""
        if not self.enabled:
            return False
        
        try:
            self.cursor.execute("SELECT 1")
            self.cursor.fetchall()
            return True
        except:
            try:
                if hasattr(self, 'cursor') and self.cursor:
                    self.cursor.close()
                if hasattr(self, 'connection') and self.connection:
                    self.connection.close()
                    
                self.connection = mysql.connector.connect(**self.db_config)
                self.cursor = self.connection.cursor()
                self.logger.info("数据库重连成功")
                return True
            except Exception as e:
                self.logger.error(f"数据库重连失败: {str(e)}")
                return False 