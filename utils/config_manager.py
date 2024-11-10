# -*- coding: utf-8 -*-
import yaml
import os
from datetime import datetime

class ConfigManager(object):
    def __init__(self, config_path="config/config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise Exception(u"加载配置文件失败: %s" % str(e))
    
    def get_csv_path(self, app_name):
        """获取CSV文件保存路径"""
        csv_dir = self.config['storage']['csv_dir']
        filename_template = self.config['storage']['filename_template']
        date_format = self.config['storage']['date_format']
        
        # 确保目录存在
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
        
        filename = filename_template.format(
            app_name=app_name,
            date=datetime.now().strftime(date_format)
        )
        
        return os.path.join(csv_dir, filename)
    
    def get_app_store_config(self):
        """获取App Store配置"""
        return self.config['app_store']
    
    def get_scraper_config(self):
        """获取爬虫配置"""
        return self.config['scraper']
    
    def get(self, key, default=None):
        return self.config.get(key, default)