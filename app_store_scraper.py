import pandas as pd
from datetime import datetime
import json
import requests
from jsonpath_ng import parse
import yaml
import os
from utils.config_manager import ConfigManager
# from app_store_module import AppStore

class AppStoreReviewScraper:
    def __init__(self, app_name, country="cn", mapping_file="config/field_mapping.yaml"):
        """
        初始化爬虫
        :param app_name: APP名称
        :param country: 国家代码，默认中国
        :param mapping_file: 字段映射配置文件路径
        """
        self.app_name = app_name
        self.country = country
        
        # 从YAML文件加载字段映射配置
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                self.field_mapping = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"找不到配置文件: {mapping_file}")
        except Exception as e:
            print(f"加载配置文件出错: {str(e)}")
        
        self.config_manager = ConfigManager()
    
    # def init_scraper(self, app_id=None):
    #     """
    #     初始化App Store爬虫
    #     :param app_id: APP的ID（可选）
    #     """
    #     self.scraper = AppStore(
    #         country=self.country,
    #         app_name=self.app_name,
    #         app_id=app_id
    #     )
    
    # def fetch_reviews(self, limit=100):
    #     """
    #     获取评论数据
    #     :param limit: 获取评论数量
    #     :return: 评论数据DataFrame
    #     """
    #     try:
    #         self.scraper.review(how_many=limit)
            
    #         # 将评论数据转换为DataFrame
    #         reviews_data = []
    #         for review in self.scraper.reviews:
    #             reviews_data.append({
    #                 '评论ID': review['review_id'],
    #                 '用户名': review['userName'],
    #                 '评分': review['rating'],
    #                 '标题': review['title'],
    #                 '内容': review['review'],
    #                 '时间': review['date'],
    #                 '版本': review['version']
    #             })
                
    #         df = pd.DataFrame(reviews_data)
    #         return df
            
    #     except Exception as e:
    #         print(f"获取评论时出错: {str(e)}")
    #         return None
    
    def save_to_csv(self, df, filename=None):
        """
        保存评论数据到CSV文件
        :param df: 评论数据DataFrame
        :param filename: 文件名
        """
        # 组合完整的文件路径
        filepath = self.config_manager.get_csv_path(filename)
        
        # 保存文件
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"数据已保存到: {filepath}")
    
    def fetch_reviews_by_url(self, url):
        # 在这里实现从URL获取评论数据的逻辑
        # 例如，使用requests库来获取数据
        response = requests.get(url)
        if response.status_code == 200:
            # 假设返回的数据是JSON格式
            data = response.json()
            # 处理数据并返回DataFrame
            # 这里需要根据实际数据结构进行解析
            return self.parse_reviews(data)
        else:
            print("无法获取评论数据，状态码:", response.status_code)
            return None

    def parse_reviews(self, data):
        if isinstance(data, str):
            data = json.loads(data)
            
        # 存储所有解析后的数据
        parsed_data = {}
        
        # 遍历配置中的所有字段组
        fields = self.field_mapping.get("app_store_review")
        for field_name, field_config in fields.items():
            path = field_config['path']
            alias = field_config['alias']
            field_type = field_config.get('type', 'str')
            
            # 使用jsonpath解析数据
            jsonpath_expr = parse(path)
            matches = [match.value for match in jsonpath_expr.find(data)]
            
            # 类型转换
            if field_type == 'int':
                matches = [int(x) if x else 0 for x in matches]
            elif field_type == 'datetime':
                # 假设日期格式是标准的ISO格式，根据实际情况可能需要调整
                matches = [pd.to_datetime(x) if x else None for x in matches]
            
            parsed_data[alias] = matches
        
        # 创建DataFrame
        df = pd.DataFrame(parsed_data)
        return df
    
    # def save_to_csv(self, df, output_file):
    #     df.to_csv(output_file, index=False, encoding='utf-8-sig')

    def load_config(self):
        with open('field_mapping.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            print("加载的原始配置:", config)  # 调试信息
            return config