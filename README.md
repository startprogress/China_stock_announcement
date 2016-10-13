# China_stock_announcement
## 简介
* 该项目通过python脚本从巨潮网络的服务器获取中国股市（sz,sh）的公告(上市公司和监管机构),把公告信息防盗数据库，公告文件下载到本地，并支持网页查询和读取。
* python用于公告下载和列表的数据库更新，node提供服务器的api调用和网页查询功能。

## 文件说明
* database：存放数据库的sql描述以及监管机构的码表
* nodejs_query： 存放node服务的代码
* python_scraw:  存放python爬虫的程序，目前有巨潮网络(cninfo.com)和中财网络(cfi.com.cn)的爬虫脚本

