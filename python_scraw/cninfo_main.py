#!/usr/bin/python
#-*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import httplib
import urllib
import urllib2
import socket
import unicodecsv
import json
import re
import calendar
import datetime
import time
import logging
import logging.handlers
import codecs
import sys
import gzip
import StringIO
import MySQLdb
from warnings import filterwarnings
filterwarnings('error', category=MySQLdb.Warning)
from bs4 import BeautifulSoup

################### 读取配置文件 ###########################
import ConfigParser  
#生成config对象  
conf = ConfigParser.ConfigParser()  
#用config对象读取配置文件  
conf.read("config.cfg")
# 赋值
filepath = conf.get('file', 'filepath')
logpath = conf.get('file', 'logpath')
host_address = conf.get('database', 'host_address')
user = conf.get('database', 'user')
password = conf.get('database', 'password')
port = int(conf.get('database', 'port'))
############################################################

############################mkdir sub path###################################
if os.path.exists(filepath) == False:
    os.makedirs(filepath)
if os.path.exists(logpath) == False:
    os.makedirs(logpath)
#############################################################################

# 把日期按日拆分后，每日都调用parse函数，解析页面，然后根据公告文件类型不同，调用不同的下载函数
def main(annc_type, start_date=datetime.datetime.today().strftime("%Y%m%d"), end_date=datetime.datetime.today().strftime("%Y%m%d"), savepath=filepath):
    if savepath[-1] != '/':
        savepath += savepath + '/'
    currentMinute = int(time.strftime('%M', time.localtime(time.time())))
    currentHour = int(time.strftime('%H', time.localtime(time.time())))
    # 当天下午2点以后要提前追一天，因为有一些公告会提前放出来
    if currentHour > 14:
        end_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y%m%d")
    global logger_error
    global logger
    # 生产日期列表
    date_range = []
    # 先变为datetime对象便于操作
    curr_date = datetime.date(
        int(start_date[0:4]), int(start_date[4:6]), int(start_date[6:8]))
    end_date = datetime.date(
        int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:8]))
    while curr_date != end_date:
        date_range.append(curr_date)
        curr_date += datetime.timedelta(days=1)
    # 再把最后一天的加上
    date_range.append(curr_date)
    # 每日循环下载,并分月建立日志(便于一次性下载很长一段时间的公告)
    log_record = []
    for datei in date_range:
        #######################################日志处理############################
        if str(datei)[0:7].replace('-', '') in log_record:
            pass
        else:
            log_record.append(str(datei)[0:7].replace('-', ''))
            # 上个月的日志关掉
            try:
                handler.flush()
                handler.close()
                logger.removeHandler(handler)
                handler_error.flush()
                handler_error.close()
                logger_error.removeHandler(handler_error)
            except:
                pass
            finally:
                # 错误日志
                if annc_type == 'sse':
                    LOG_ERROR_FILE = logpath + \
                        str(datei)[0:7].replace('-', '') + '_error.log'
                if annc_type == 'regulator':
                    LOG_ERROR_FILE = logpath + \
                        str(datei)[0:7].replace('-', '') + '_error.log'

                handler_error = logging.handlers.RotatingFileHandler(
                    LOG_ERROR_FILE, maxBytes=1024 * 1024, backupCount=5)  # 实例化handler
                fmt_error = '%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s'
                formatter_error = logging.Formatter(fmt_error)  # 实例化formatter
                handler_error.setFormatter(
                    formatter_error)      # 为handler添加formatter
                logger_error = logging.getLogger(
                    'annc_error')    # 获取名为content的logger
                # 为logger添加handler
                logger_error.addHandler(handler_error)
                logger_error.setLevel(logging.ERROR)

                # INFO日志处理
                if annc_type == 'sse':
                    LOG_INFO_FILE = logpath + \
                        str(datei)[0:7].replace('-', '') + '_info.log'
                if annc_type == 'regulator':
                    LOG_INFO_FILE = logpath + \
                        str(datei)[0:7].replace('-', '') + '_info.log'

                handler = logging.handlers.RotatingFileHandler(
                    LOG_INFO_FILE, maxBytes=1024 * 1024, backupCount=5)  # 实例化handler
                fmt = '%(asctime)s  - %(levelname)s - %(message)s'
                formatter = logging.Formatter(fmt)  # 实例化formatter
                handler.setFormatter(formatter)      # 为handler添加formatter
                logger = logging.getLogger('annc_info')    # 获取名为content的logger
                logger.addHandler(handler)          # 为logger添加handler
                logger.setLevel(logging.INFO)
        # 按日下载
        parse(annc_type, datei, savepath)



####################################################下载公告列表，解析并下载公告########
def parse(columntype, daterange_i, downloadpath):
    # 检查路径，若没有即创建
    if columntype == 'sse':
        contentpath = downloadpath + 'sse/content/' + \
            str(daterange_i)[0:4] + '/' + str(daterange_i)[5:7] + '/'
        listpath = downloadpath + 'sse/list/' + \
            str(daterange_i)[0:4] + '/'
    if columntype == 'regulator':
        contentpath = downloadpath + 'reg/content/' + \
            str(daterange_i)[0:4] + '/' + str(daterange_i)[5:7] + '/'
        listpath = downloadpath + 'reg/list/' + \
            str(daterange_i)[0:4] + '/'
        columntype = 'regulator'
    if os.path.exists(contentpath) == False:
        os.makedirs(contentpath)
    if os.path.exists(listpath) == False:
        os.makedirs(listpath)
    # 服务器地址starturl
    starturl = 'http://www.cninfo.com.cn/cninfo-new/announcement/query'

    ############################################ list 部分 #####################
    # 读取最新的URL列表, 放入now []
    now = []
    # 字典d用于得到每只股票的当日anncid
    d = dict()  # 用于形成anncid里的序号
    flag = True  # 用于确认是否有下一页的布尔值
    page_num = 1  # 起始页为1
    while flag == True:
        # request headers
        headers = {
            "Host": "www.cninfo.com.cn",
            "Connection": "keep-alive",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "http://www.cninfo.com.cn",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://www.cninfo.com.cn/cninfo-new/announcement/show",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6"
        }

        # request data
        datas = []
        sse_data = 'stock=&searchkey=&plate=&category=&trade=&column=' + columntype + '&columnTitle=%E5%8E%86%E5%8F%B2%E5%85%AC%E5%91%8A%E6%9F%A5%E8%AF%A2&pageNum=' + \
            str(page_num) + '&pageSize=30&tabName=fulltext&sortName=&sortType=&limit=&showTitle=&seDate=' + str(daterange_i)

        jgjg_sz_data = 'stock=&searchkey=' + '&plate=jgjg_sz%3B' +'&category=&trade=&column=' + columntype + '&columnTitle=%E5%8E%86%E5%8F%B2%E5%85%AC%E5%91%8A%E6%9F%A5%E8%AF%A2&pageNum=' + \
            str(page_num) + '&pageSize=30&tabName=fulltext&sortName=&sortType=&limit=&showTitle=jgjg_sz%2Fplate%2F%E6%B7%B1%E4%BA%A4%E6%89%80%E5%85%AC%E5%91%8A&seDate=' + str(daterange_i)
        jgjg_sh_data = 'stock=&searchkey=' + '&plate=jgjg_sh%3B' + '&category=&trade=&column=' + columntype + '&columnTitle=%E5%8E%86%E5%8F%B2%E5%85%AC%E5%91%8A%E6%9F%A5%E8%AF%A2&pageNum=' + \
            str(page_num) + '&pageSize=30&tabName=fulltext&sortName=&sortType=&limit=&showTitle=jgjg_sh%2Fplate%2F%E4%B8%8A%E4%BA%A4%E6%89%80%E5%85%AC%E5%91%8A&seDate=' + str(daterange_i)
        jgjg_jsgs_data = 'stock=&searchkey=' + '&plate=jgjg_jsgs%3B' + '&category=&trade=&column=' + columntype + '&columnTitle=%E5%8E%86%E5%8F%B2%E5%85%AC%E5%91%8A%E6%9F%A5%E8%AF%A2&pageNum=' + \
            str(page_num) + '&pageSize=30&tabName=fulltext&sortName=&sortType=&limit=&showTitle=jgjg_jsgs%2Fplate%2F%E7%BB%93%E7%AE%97%E5%85%AC%E5%8F%B8%E5%85%AC%E5%91%8A&seDate=' + str(daterange_i)
        jgjg_zjh_data = 'stock=&searchkey=' + '&plate=jgjg_zjh%3B' + '&category=&trade=&column=' + columntype + '&columnTitle=%E5%8E%86%E5%8F%B2%E5%85%AC%E5%91%8A%E6%9F%A5%E8%AF%A2&pageNum=' + \
            str(page_num) + '&pageSize=30&tabName=fulltext&sortName=&sortType=&limit=&showTitle=jgjg_zjh%2Fplate%2F%E8%AF%81%E7%9B%91%E4%BC%9A%E5%85%AC%E5%91%8A&seDate=' + str(daterange_i)


        if columntype == 'regulator':
            datas.append(jgjg_sz_data)
            datas.append(jgjg_sh_data)
            datas.append(jgjg_jsgs_data)
            datas.append(jgjg_zjh_data)
        elif columntype == 'sse':
            datas.append(sse_data)
        for data in datas:
            req = urllib2.Request(starturl, data, headers)
            try:
                response = urllib2.urlopen(req)

            except urllib2.HTTPError, e:
                logger_error.error('响应错误 日期 页数: %s %s %s' %
                                   (e, str(daterange_i), str(page_num)))
                flag = False
            except urllib2.URLError, e:
                logger_error.error('响应错误 日期 页数: %s %s %s' %
                                   (e, str(daterange_i), str(page_num)))
                flag = False
            except socket.error, e:
                logger_error.error('响应错误 日期 页数: %s %s %s' %
                                   (e, str(daterange_i), str(page_num)))
                flag = False
            else:
                # 需要将response解压缩
                # 参考: https://www.cnblogs.com/bbcar/p/3625084.html
                res_data = StringIO.StringIO(response.read())
                rzip = gzip.GzipFile(fileobj = res_data)
                r = rzip.read()
                try:
                    # 将相应json化便于用字典读取
                    j = json.loads(r)
                except ValueError, e:
                    logger_error.error('响应错误 日期 页数: %s %s %s' %
                                       (e, str(daterange_i), str(page_num)))
                    flag = False
                else:
                    flag = j['hasMore']
                    # 记录日志
                    logger.info('日 期:' + str(daterange_i) + '     PageNUmber = ' + str(page_num) +
                                '   hasMore = ' + str(flag))
                    # 把每一页的项目append 到now里
                    for item_num in range(0, len(j['announcements'])):
                        ii = j['announcements'][item_num]
                        valid = 0  # 下载成功后变为1
                        # 得到 title url 和 file_type
                        title = ii['announcementTitle'].replace(',', '').replace(
                            '<font color=red>', '').replace('</font>', '').replace('\n', '')
                        url = 'http://www.cninfo.com.cn/' + \
                            ii['adjunctUrl'].strip()
                        # 防止重复
                        if (url in d) == False:
                            d[url] = 'Yes'
                            ########################确定公告文件的类型file_type#############
                            if url.find('.html') > -1:
                                file_type = 'TXT'
                            elif url.find('.js') > -1:
                                file_type = 'TXT'
                            elif url.find('.pdf') > -1 or url.find('.PDF') > -1:
                                file_type = 'PDF'
                            elif url.find('.doc') > -1 or url.find('.DOC') > -1:
                                if url.find('.docx') > -1 or url.find('.DOCX') > -1:
                                    file_type = 'DOCX'
                                else:
                                    file_type = 'DOC'
                            else:
                                file_type = 'UNKNOEN'
                            #######################################################
                            # 把时间戳转为yyyy-mm-dd hh:mm:ss的形式，若没有，则按00:00:00算
                            try:
                                antime = time.strftime(
                                    '%Y-%m-%d %H:%M:%S', time.localtime(ii['announcementTime'] / 1000))
                            except ValueError, e:
                                antime = daterange_i + ' 00:00:00'
                            else:
                                pass
                            if columntype == 'sse':
                                abbv = ii['secName']
                                symbol = ii['secCode']
                                # 生成anncid
                                if len(symbol) == 6:
                                    if symbol in d:
                                        d[symbol] = int(d[symbol]) + 1
                                    else:
                                        d[symbol] = 1
                                # 1位数字添00,2位数字添0
                                    if d[symbol] < 10:
                                        anncid = symbol + \
                                            str(daterange_i).replace(
                                                '-', '') + '00' + str(d[symbol])
                                    elif d[symbol] < 100:
                                        anncid = symbol + \
                                            str(daterange_i).replace(
                                                '-', '') + '0' + str(d[symbol])
                                    else:
                                        anncid = symbol + \
                                            str(daterange_i).replace(
                                                '-', '') + str(d[symbol])
                                    anncid = str(anncid)

                                    now.append([anncid, symbol, abbv, title, antime[
                                               0:10], antime[-8:], file_type, url, valid, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                            elif columntype == 'regulator':
                                symbol = ii['secCode'].replace(',', ';')
                                # 根据查询参数来确定公告类型
                                if data.find('jgjg_sz') > -1:
                                    regu_type = 'SZSE'
                                elif data.find('jgjg_sh') > -1:
                                    regu_type = 'SSE'
                                elif data.find('plate=jgjg_jsgs') > -1:
                                    regu_type = 'CSDC'
                                elif data.find('jgjg_zjh') > -1:
                                    regu_type = 'CSRC'
                                if regu_type in d:
                                    d[regu_type] = int(d[regu_type]) + 1
                                else:
                                    d[regu_type] = 1
                                # 个位数字添0
                                if d[regu_type] < 10:
                                    anncid = regu_type + \
                                        str(daterange_i).replace(
                                            '-', '') + '0' + str(d[regu_type])
                                else:
                                    anncid = regu_type + \
                                        str(daterange_i).replace(
                                            '-', '') + str(d[regu_type])
                                now.append([anncid, symbol, regu_type, title, antime[
                                    0:10], antime[-8:], file_type, url, valid, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

                    page_num += 1
                response.close()

    # 如果没有数据则不进行后续工作
    if len(now) != 0:
        # 把已存文件的内容读出来，作为old [],若当日无csv则创建，old置空
        old = []
        temp = []
        if os.path.exists(listpath + str(daterange_i) + '.csv'):
            f_old = open(listpath + str(daterange_i) + '.csv', 'r+')
            f_r = unicodecsv.reader(f_old, encoding='utf-8')
            for row in f_r:
                old.append(row)
            f_old.close()
            # 把now中与old重复的去掉,计入temp
            for i in now:
                has = False
                for j in old:
                    if i[7].strip() == j[7].strip():
                        has = True
                if has == False:
                    temp.append(i)
        else:
            temp = now

        #########################################download部分####################
        # 如果有新的，就更新到csv和数据库里
        if len(temp) != 0:
            # 把temp中url指向的公告下载到contentpath下,并更新temp到tempupdate
            temp_update = []
            # temp里的公告都尝试下载，并根据是否成功下载，更新为temp_updata
            for row in temp:
                url = row[7]
                anncid = row[0]
                # 解析url类型并下载url链接下的公告
                # 根据是否成功下载 更新valid字段的值
                if url.find('.html') > -1 and downhtml(contentpath, anncid, url):
                    row[8] = 1
                elif url.find('.js') > -1 and downjs(contentpath, anncid, url):
                    row[8] = 1
                elif (url.find('.doc') > -1 or url.find('.DOC') > -1) and downdoc(contentpath, anncid, url):
                    row[8] = 1
                elif (url.find('.pdf') > -1 or url.find('.PDF') > -1) and downpdf(contentpath, anncid, url):
                    row[8] = 1
                else:
                    logger_error.error(
                        '公告新类型未下载： id号 URL网址: %s %s' % (anncid, url))
                temp_update.append(row)
            logger.info('本次成功下载了' + str(len(temp_update)) + '份公告')

            # 把之前未存的temp 里的数据 更新到月csv 和 日csv, 日csv里的内容作为下次的 old[]
            f_mon = open(listpath + str(daterange_i)
                         [0:7].replace('-', '') + '.csv', 'a+')
            f_w = unicodecsv.writer(
                f_mon, encoding='utf-8')  # 直接使用csv则存储的都是二进制
            for row in temp_update:
                f_w.writerow(row)
            f_mon.close()
            f_day = open(listpath + str(daterange_i) + '.csv', 'a+')
            f_w = unicodecsv.writer(
                f_day, encoding='utf-8')  # 直接使用csv则存储的都是二进制
            for row in temp_update:
                f_w.writerow(row)
            f_day.close()
            f_tmp = open(listpath + str(daterange_i) + '_temp.csv', 'a+')
            f_w = unicodecsv.writer(
                f_tmp, encoding='utf-8')  # 直接使用csv则存储的都是二进制
            for row in temp_update:
                f_w.writerow(row)
            f_tmp.close()

            #把更新的数据倒入数据库中 ,然后把temp.csv删掉
            if columntype == 'sse':
                import2mysql(columntype, listpath +
                             str(daterange_i) + '_temp.csv', 'sse_annc_list')
            if columntype == 'regulator':
                import2mysql(columntype, listpath +
                             str(daterange_i) + '_temp.csv', 'reg_annc_list')
                #公告影响表
                impact = []
                f_impact = open(listpath + 'impact.csv', 'a+')
                f_w = unicodecsv.writer(
                    f_impact, encoding='utf-8')  # 直接使用csv则存储的都是二进制
                for row in temp_update:
                    if len(row[0]) > 3 and row[1] != None and row[1] != '':
                        impact_i = row[1].strip('\n').split(';')
                        for imp in impact_i:
                            if imp != '':
                                impact.append([row[0], imp])
                for item in impact:
                    f_w.writerow(item)
                f_impact.close()
                import2mysql(columntype, listpath +
                             'impact.csv', 'reg_impact_list')
                os.remove(listpath + 'impact.csv')
            os.remove(listpath + str(daterange_i) + '_temp.csv')


def import2mysql(columntype, csvfile, tablename):
    if columntype == 'sse':
        LOG_FILE = logpath + 'sse_mysql.log'
    if columntype == 'regulator':
        LOG_FILE = logpath + 'regu_mysql.log'
    handler_mysql = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=1024 * 1024, backupCount=5)  # 实例化handler
    fmt_mysql = '%(asctime)s  - %(message)s'
    formatter_mysql = logging.Formatter(fmt_mysql)   # 实例化formatter
    handler_mysql.setFormatter(formatter_mysql)      # 为handler添加formatter
    logger_mysql = logging.getLogger('mysql')    # 获取名为import的logger
    logger_mysql.addHandler(handler_mysql)           # 为logger添加handler
    logger_mysql.setLevel(logging.DEBUG)
    # 连接数据库
    try:
        conn = MySQLdb.connect(host=host_address, user=user,
                               passwd=password, port=port)
        cur = conn.cursor()
    except MySQLdb.Error, e:
        logger_mysql.error("MySQL数据连接不上 %s" % (str(e)))
    else:
        # datebase stock
        cur.execute('use stock;')
        sql = "load data local infile " + "'" + csvfile + "'" + \
            " into table " + tablename + " fields terminated by ',' lines terminated by '\n';"
        try:
            cur.execute(sql)  # 执行sql语句
            conn.commit()  # 提交
        except MySQLdb.Warning:
            cur.execute("SHOW WARNINGS")
            w = cur.fetchall()
            for i in w:
                logger_mysql.info(" %s" % (i,))
        except MySQLdb.Error, e:
            logger_mysql.error("数据导入mysql错误 %s %s" % (csvfile, str(e),))
        else:
            logger_mysql.info("处理文件成功 %s" % (csvfile, ))  # 操作成功
        # 关闭日志
        handler_mysql.flush()
        handler_mysql.close()
        logger_mysql.removeHandler(handler_mysql)
        cur.close()  # 关闭操作
        conn.close()  # 关闭连接

#把html网页的文字下载到txt中
def downhtml(contentpath, anncid, url):
    flag = False
    try:
        contentpage = urllib2.urlopen(url)
    except urllib2.URLError, e:
        logger_error.error(
            '公告链接错误 id号 URL网址: %s %s %s' % (e, anncid, url))
    except socket.timeout:
        downhtml(contentpath, anncid, url)
    except socket.error, e:
        if str(e).find('Connection reset by peer') or str(e).find('Operation timed out') != -1:
            downhtml(contentpath, anncid, url)
        else:
            logger_error.error(
                '公告链接错误 id号 URL网址: %s %s %s' % (e, anncid, url))
    else:
        contentsoup = BeautifulSoup(
            contentpage, 'lxml', from_encoding="utf-8")
        try:
            content = contentsoup.findAll(
                'span', {'class': 'da'})
            con_len = len(content)
            content_txt = content[
                con_len - 1].get_text()
        except IndexError, e:
            try:
                content = contentsoup.findAll(
                    'pre')
                con_len = len(content)
                content_txt = content[0].get_text()
            except IndexError, e:
                logger_error.error(
                    '页面解析错误 id号 URL网址: %s %s %s' % (e, anncid, url))
            else:
                f_temp = codecs.open(
                    contentpath + anncid + '.txt', 'w+', encoding='utf-8')
                f_temp.write(content_txt)
                f_temp.close()
                logger.info('成功下载： id为：%s url：%s ' %
                            (anncid, url))
                flag = True
        else:
            f_temp = codecs.open(
                contentpath + anncid + '.txt', 'w+', encoding='utf-8')
            f_temp.write(content_txt)
            f_temp.close()
            logger.info('成功下载： id为：%s url：%s ' % (anncid, url))
            flag = True
    finally:
        if 'contentpage' in locals().keys():
            contentpage.close()
        return flag

##把js返回的文字下载到txt中
def downjs(contentpath, anncid, url):
    flag = False
    try:
        contentpage = urllib2.urlopen(url)
        content_txt = contentpage.read()
    except urllib2.URLError, e:
        logger_error.error(
            '公告链接错误 id号 URL网址: %s %s %s' % (e, anncid, url))
    except socket.timeout:
        downjs(contentpath, anncid, url)
    except socket.error, e:
        if str(e).find('Connection reset by peer') or str(e).find('Operation timed out') != -1:
            downjs(contentpath, anncid, url)
        else:
            logger_error.error(
                '公告链接错误 id号 URL网址: %s %s %s' % (e, anncid, url))
    else:
        try:
            content_txt = content_txt.decode('gbk').encode('utf-8')
        except UnicodeDecodeError, e:
            logger_error.error(
                'js类型解码错误 id号 URL网址: %s %s %s' % (e, anncid, url))
        else:
            content_txt = re.search(
                r'"Zw":(.*)<br>', content_txt)
            if content_txt == None:
                logger_error.error(
                    'js类型解码错误 id号 URL网址: %s %s' % (anncid, url))
            else:
                content_txt = content_txt.group().replace('<br>', '').replace('"Zw":"', '')
                f_temp = codecs.open(
                    contentpath + anncid + '.txt', 'w+', encoding='utf-8')
                f_temp.write(content_txt)
                f_temp.close()
                logger.info('成功下载： id为：%s url：%s ' %
                            (anncid, url))
                flag = True   
    finally:
        if 'contentpage' in locals().keys():
            contentpage.close()
        return flag
        
##下载doc
def downdoc(contentpath, anncid, url):
    flag = False
    try:
        contentpage = urllib2.urlopen(url)
        content_doc = contentpage.read()
    except urllib2.URLError, e:
        logger_error.error(
            '公告链接错误 id号 URL网址: %s %s %s' % (e, anncid, url))
    except urllib2.URLError, e:
        logger_error.error(
            '公告链接错误 id号 URL网址: %s %s %s' % (e, anncid, url))
    except httplib.BadStatusLine, e:
        logger_error.error(
            '公告链接错误 id号 URL网址: %s %s %s' % (e, anncid, url))
    except socket.timeout:
        downdoc(contentpath, anncid, url)
    except socket.error, e:
        if str(e).find('Connection reset by peer') or str(e).find('Operation timed out') != -1:
            downdoc(contentpath, anncid, url)
        else:
            logger_error.error(
                '公告链接错误 id号 URL网址: %s %s %s' % (e, anncid, url))
    else:
        if url.find('.docx') > -1 or url.find('.DOCX') > -1:
            f_temp = open(
                contentpath + anncid + '.docx', 'w+')
        else:
            f_temp = open(
                contentpath + anncid + '.doc', 'w+')
        f_temp.write(content_doc)
        f_temp.close()
        logger.info('成功下载： id为：%s url：%s ' % (anncid, url))
        flag =True
    finally:    
        if 'contentpage' in locals().keys():
            contentpage.close()
        return flag

##下载pdf
def downpdf(contentpath, anncid, url):
    flag = False
    try:
        contentpage = urllib2.urlopen(url)
        content_pdf = contentpage.read()

    except httplib.BadStatusLine, e:
        logger_error.error(
            '公告链接错误 id号 URL网址: %s %s %s' % (e, anncid, url))

    except socket.timeout:
        downpdf(contentpath, anncid, url)
    except socket.error, e:
        if str(e).find('Connection reset by peer') or str(e).find('Operation timed out') != -1:
            downpdf(contentpath, anncid, url)
        else:
            logger_error.error(
                '公告链接错误 id号 URL网址: %s %s %s' % (e, anncid, url))
    else:
        f_temp = open(
            contentpath + anncid + '.pdf', 'w+')
        f_temp.write(content_pdf)
        f_temp.close()
        logger.info('成功下载： id为：%s url：%s ' % (anncid, url))
        flag = True
    finally:
        if 'contentpage' in locals().keys():
            contentpage.close()
        return flag
        
if __name__ == "__main__":
    if len(sys.argv) == 4:  # 按照参数执行，由于python程序本身（***.py）就是argv[0]，所以下标需要从1开始
        main(annc_type=sys.argv[1], start_date=sys.argv[
                           2], end_date=sys.argv[3])
    elif len(sys.argv) == 3:
        main(annc_type=sys.argv[1], start_date=sys.argv[
                           2], end_date=sys.argv[2])
    elif len(sys.argv) == 2:
        main(annc_type=sys.argv[1])
    else:
        print '参数输入不正确'