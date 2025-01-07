import json
from tencentcloud.tag.v20180813 import tag_client, models

class TagService:
    def __init__(self, cred, region, client_profile):
        self.client = tag_client.TagClient(cred, region, client_profile)

    def get_project_name(self, project_id):
        """获取项目名称"""
        try:
            req = models.DescribeProjectsRequest()
            params = {
                "AllList": 1,
                "Limit": 100,
                "Offset": 0,
                "ProjectId": project_id
            }
            req.from_json_string(json.dumps(params))
            resp = self.client.DescribeProjects(req)
            resp_dict = json.loads(resp.to_json_string())
            
            if "Projects" in resp_dict and resp_dict["Projects"]:
                return resp_dict["Projects"][0]["ProjectName"]
                
            print(f"未找到项目 ID {project_id} 对应的项目名称")
            return None
            
        except Exception as e:
            print(f"获取项目名称时发生错误: {str(e)}")
            return None 