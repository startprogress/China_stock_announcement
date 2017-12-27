# annc

## 简介
* 该项目旨在替代cninfo_main.py, 用scrapy框架完成
* 从巨潮网络的服务器获取中国股市公告，元数据存入MySQL，公告文件下载到本地
* 目前只支持上市公司，功能会逐渐完善

## 使用
* 准备好scrapy环境
* 参考cninfo_main.py 中的数据表建表
* 在 annc//settings.py中，修改文件路径和数据库配置
* 在annc/路径下，执行 scrapy crawl annc -a annc_type="sse" -a date_range="20171227" 或 scrapy crawl annc -a annc_type="sse" -a date_range="20171221~20171231"可进行爬取