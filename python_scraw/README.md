### 该脚本从巨潮网络的服务器上将公告下载，把每条公告的相关信息存入数据库中。

### 公告命名方法为：
* 上市公司：股票代码（6位）+YYYYMMDD(8位)+ 当日当支股票公告的排序号(3位)
* 监管公告：监管代码(3或4位) ＋ YYYYMMDD（8位） ＋ 序号(2位)

### 参数介绍
* python cninfo_main.py sse(regulator) [startdate] [enddate]
* sse是公司公告，regulator是监管机构公告，每次只能下载一种
* 无时间参数默认为当天数据，若要下一个区间的数据，则需要startdate，enddate两个参数，如果指明非今天的某一天，则只写一个参数即可
* date的格式YYYYMMDD
* 示例： 下载2017年1月1号到3月31号的公司公告: python cninfo_main.py sse 20170101 20170331
* 示例： 下载2017年1月1号当天的监管公告： python cninfo_main.py regulator 20170101