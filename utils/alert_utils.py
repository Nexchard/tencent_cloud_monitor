from typing import List, Dict

def filter_resources_by_days(resources: List[Dict], alert_config: Dict) -> List[Dict]:
    """
    根据告警配置过滤需要告警的资源
    
    :param resources: 资源列表
    :param alert_config: 告警配置
    :return: 过滤后的资源列表
    """
    if alert_config['resource_alert_mode'] == 'all':
        return resources
        
    return [
        resource for resource in resources 
        if resource.get('DifferDays', 0) <= alert_config['resource_alert_days']
    ] 