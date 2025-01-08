from typing import List, Dict

def filter_resources_by_days(resources, days):
    """根据剩余天数过滤资源"""
    if not resources:
        return []
    
    return [
        resource for resource in resources 
        if resource.get('DifferDays', 0) <= days
    ] 