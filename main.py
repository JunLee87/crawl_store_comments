# -*- coding: utf-8 -*-
from app_store_scraper import AppStoreReviewScraper
from utils.config_manager import ConfigManager

def print_app_list(apps):
    """打印APP列表"""
    print(u"\n找到以下匹配的APP：")
    print("-" * 80)
    print(u"%-6s%-12s%-20s%-20s%s" % (u"序号", u"APP ID", u"名称", u"开发者", u"描述"))
    print("-" * 80)
    
    for i, app in enumerate(apps, 1):
        print(u"%-6d%-12s%-20s%-20s%s" % (
            i,
            app['id'],
            app['name'][:18],
            app['developer'][:18],
            app['description'][:30]
        ))

def main():
    # 初始化配置管理器
    config = ConfigManager()
    
    # 创建爬虫实例
    scraper = AppStoreReviewScraper(config)
    
    # 选择操作模式
    print(u"1. 通过APP名称搜索")
    print(u"2. 使用配置文件中的APP ID")
    choice = input(u"请选择操作模式 (1/2): ")
    
    if choice == "1":
        # 搜索APP
        app_name = input(u"请输入要搜索的APP名称: ")
        country = input(u"请输入国家代码(直接回车默认cn): ") or "cn"
        
        apps = scraper.search_app_id(app_name, country)
        
        if not apps:
            print(u"未找到匹配的APP")
            return
        
        print_app_list(apps)
        
        # 选择APP
        while True:
            try:
                choice = int(input(u"\n请选择要爬取的APP序号(输入0退出): "))
                if choice == 0:
                    return
                if 1 <= choice <= len(apps):
                    selected_app = apps[choice-1]
                    break
                print(u"无效的选择，请重试")
            except ValueError:
                print(u"请输入有效的数字")
                
        # 构造评论URL
        app_id = selected_app['id']
        url = "https://itunes.apple.com/rss/customerreviews/page=1/id=%s/sortby=mostrecent/json?l=en&&cc=%s" % (app_id, country)
        
    else:
        # 从配置文件中读取APP ID
        app_id = config.get('app_id')
        country = config.get('country', 'cn')
        app_name = input(u"请输入APP名称(用于保存文件): ")
        
        # 构造评论URL
        url = "https://itunes.apple.com/rss/customerreviews/page=1/id=%s/sortby=mostrecent/json?l=en&&cc=%s" % (app_id, country)
    
    # 获取评论数据
    reviews_df = scraper.fetch_reviews_by_url(url)
    
    if reviews_df is not None:
        # 保存到CSV文件
        scraper.save_to_csv(reviews_df, app_name)

if __name__ == "__main__":
    main()
