# China_stock_announcement
## 简介
* 该项目通过python脚本从巨潮网络的服务器获取中国股市公告(上市公司和监管机构),公告信息存入数据库，公告文件下载到本地
* 还可支持文本抽取, 网页，API的查询和读取等功能
* python实现公告爬取下载，nodejs搭建网络服务，提供api和网页展示

## 文件说明
* database/: 存放数据库的sql文件，可以用shell命令执行，创建数据库和数据表
* nodejs_query/: 存放node服务的代码
* python_scraw/:  存放python爬虫的程序, cninfo_main.py可实现较为全面的功能，annc文件下是用scrapy框架写的爬虫，正在逐渐完善，以后会替代cninfo_main.py
* 2plaintext/: 存放一个python小脚本，用于将pdf、doc、docx文件转为纯文本文件

## 使用
* 准备好MySQL，Python等环境, 参考python_scraw/cninfo_main.py的头引入，下载一些python包
* 进入 database/ 执行 mysql -u $USER -p$PASSWORD <database.sql，创建数据库和数据表
* 在python_scraw/config中，修改文件路径和数据库配置
* 执行python cninfo_main.py 进行下载，参数介绍见 python_scraw/README.md

## 附加 
* 如需提供静态网站展示，可以用nodejs_query中的代码启动一个服务
* 2plaintext/ 下的程序可以抽取纯文本

## 版本说明
本项目使用Python2.7
