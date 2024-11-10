# -*- coding: utf-8 -*-
import json
from datetime import datetime
import yaml
import jsonpath
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class DataParser(object):
    def __init__(self, mapping_file="config/field_mapping.yaml"):
        """
        初始化数据解析器
        :param mapping_file: 字段映射配置文件路径
        """
        self.mapping = self._load_mapping(mapping_file)
        
    def _load_mapping(self, mapping_file):
        """加载字段映射配置"""
        with open(mapping_file, 'r') as f:
            return yaml.safe_load(f)
    
    def parse_app_store_review(self, json_data):
        """
        解析App Store评论数据
        :param json_data: JSON格式的评论数据
        :return: 解析后的评论数据列表
        """
        try:
            # 解析JSON数据
            data = json.loads(json_data)
            mapping = self.mapping['app_store_review']
            
            # 提取所有评论
            reviews = []
            
            # 获取评论总数
            entries = jsonpath.jsonpath(data, 'feed.entry[*]')
            if not entries:
                return []
                
            for i in xrange(len(entries)):  # 使用xrange替代range
                review = {}
                
                # 遍历配置中的所有字段
                for category in mapping.values():
                    for field_name, field_config in category.iteritems():  # 使用iteritems替代items
                        path = field_config['path'].replace('[*]', '[%d]' % i)
                        value = jsonpath.jsonpath(data, path)
                        
                        if value:
                            value = value[0]
                            # 根据配置进行类型转换
                            if 'type' in field_config:
                                value = self._convert_type(value, field_config['type'])
                                
                            review[field_config['alias']] = value
                
                reviews.append(review)
                
            return reviews
            
        except Exception as e:
            print(u"解析数据时出错: %s" % unicode(e))
            return []
            
    def _convert_type(self, value, type_name):
        """
        转换数据类型
        :param value: 原始值
        :param type_name: 目标类型名称
        :return: 转换后的值
        """
        try:
            if type_name == 'int':
                return int(value)
            elif type_name == 'float':
                return float(value)
            elif type_name == 'datetime':
                return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S-07:00')
            return value
        except:
            return value