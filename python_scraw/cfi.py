# -*- coding: utf-8 -*-
import urllib
import urllib2
import json
import codecs
import unicodecsv
import datetime
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from bs4 import BeautifulSoup


def get_url():
    content = urllib2.urlopen('http://data.cfi.cn/cfidata.aspx?fr=menu').read()
    contentsoup = BeautifulSoup(content, 'lxml', from_encoding="utf-8")
    classname = ''

    def lookup(beautifulObj, classnum, divname):
        return_result = ''
        if int(classnum) == len(sys.argv) - 1:
            result = beautifulObj.findAll(
                'div', {'class': 't' + str(classnum)})
            if result == []:
                result = beautifulObj.findAll('div', {'class': 'b'})
            for i in range(0, len(result)):
                if str(result[i]).find(divname) > -1:
                    if result[i].a['href'].find('http') > -1:
                        return_result = result[i].a['href']
                    else:
                        return_result = 'http://data.cfi.cn/' + \
                            result[i].a['href']
        else:
            result = beautifulObj.findAll(
                'div', {'class': 't' + str(classnum)})
            for i in range(0, len(result)):
                if str(result[i]).find(divname) > -1:

                    return_result = beautifulObj.findAll(
                        'div', {'class': 'd' + str(classnum)})[i]
        if return_result == '':
            return '输入有误'
        else:
            return return_result

    for i in range(1, len(sys.argv)):
        classname = 't' + str(i)
        if contentsoup == '输入有误':
            break
        else:
                # 为了便于递归
            contentsoup = lookup(contentsoup, i, sys.argv[i])
    # 如果顺利找到网址，contentsoup即为url，否则为输入有误
    url = contentsoup
    # 判断是否找到url，若找到的话从首页上寻找后续页面的url，没找到则直接返回输入有误的信息
    if url.find('http') > -1:
        urls = []
        urls.append(url)
        content = urllib2.urlopen(url).read()
        contentsoup = BeautifulSoup(
            content, 'lxml', from_encoding="utf-8").findAll(id="content")[0]
        urlcontent = contentsoup.findAll('div')[1].findAll('a')
        # 减1 是避免把"下一页"的内容当作最后一页的内容读进来,看一下网页结构更容易理解
        for i in range(0, len(urlcontent) - 1):
            urls.append('http://data.cfi.cn/' + urlcontent[i]['href'])
        return urls
    else:
        # 此时为'输入有误‘
        print url
        return url



def get_data(urls):
    if urls != '输入有误':
        def write2csv(csvpath, csvfile, content, first_Flag):
            sheet = []
            # 把详细仓位的表头添加进去，其表头信息不含在tr标签内，故需要特殊处理
            if csvpath.find('详细仓位') > -1:
                num = len(content.findAll('tr')[0].findAll('td'))
                titlecontent = content.findAll('td')
                title = []
                for i in range(0, num):
                    title.append(titlecontent[i].get_text())
                sheet.append(title)
            content = content.findAll('tr')

            if first_Flag == True:
                # 把包括表头在内的读到一个list
                for row in content:
                    tds = row.findAll('td')
                    sheet_item = []
                    for column in range(0, len(tds)):
                        sheet_item.append(tds[column].get_text())
                        if tds[column].get_text() == '详细仓位' and tds[column].a != None:
                            detailcontent = urllib2.urlopen(
                                'http://data.cfi.cn/' + tds[column].a['href']).read()
                            detailsoup = BeautifulSoup(
                                detailcontent, 'lxml', from_encoding="utf-8").findAll(id='datatable')[0]
                            detailpath = csvpath + '详细仓位' + '/'
                            if os.path.exists(detailpath) == False:
                                os.makedirs(detailpath)
                            detailfile = str(
                                tds[0].get_text()) + str(tds[2].get_text()).replace('-', '') + '.csv'
                            write2csv(detailpath, detailfile, detailsoup, True)
                    sheet.append(sheet_item)
            else:
                for row in range(1, len(content)):
                    # 除表头外的内容读到list
                    tds = content[row].findAll('td')
                    sheet_item = []
                    for column in range(0, len(tds)):
                        sheet_item.append(tds[column].get_text())
                        if tds[column].get_text() == '详细仓位' and tds[column].a != None:
                            detailcontent = urllib2.urlopen(
                                'http://data.cfi.cn/' + tds[column].a['href']).read()
                            detailsoup = BeautifulSoup(
                                detailcontent, 'lxml', from_encoding="utf-8").findAll(id='datatable')[0]
                            detailpath = csvpath + '详细仓位' + '/'
                            if os.path.exists(detailpath) == False:
                                os.makedirs(detailpath)
                            detailfile = str(
                                tds[0].get_text()) + str(tds[2].get_text()).replace('-', '') + '.csv'
                            write2csv(detailpath, detailfile, detailsoup, True)
                    sheet.append(sheet_item)
            with open(csvpath + csvfile, 'a+') as f:
                f_w = unicodecsv.writer(f, encoding='utf-8')
                for i in sheet:
                    f_w.writerow(i)

        # 路径和文件名的赋值
        csvpath = '/data/cfi/'
        for i in range(1, len(sys.argv)):
            csvpath += sys.argv[i] + '/'
        if os.path.exists(csvpath) == False:
            os.makedirs(csvpath)
        csvfile = sys.argv[len(sys.argv) - 1] + '_' + \
            str(datetime.date.today()).replace('-', '') + '.csv'

        # 循环将urls里的网址所包含的数据下载
        for i in range(0, len(urls)):
            content = urllib2.urlopen(urls[i]).read()
            contentsoup = BeautifulSoup(
                content, 'lxml', from_encoding="utf-8").findAll(id="content")[0]
            sheetcontent = contentsoup.findAll('table', {'class', 'table_data'})[
                0]
            if i == 0:
                write2csv(csvpath, csvfile, sheetcontent, True)
            else:
                write2csv(csvpath, csvfile, sheetcontent, False)


def cfi_data():
    # 通过多级目录找到所需数据首页的url，并把所有页面的url都找到
    urls = get_url()
    try:
        # urls里网址所包含的数据都下载到csv里
        get_data(urls)
    except:
        print '抓取有错误'
    else:
        print '抓取完成'


# 调用了cninfoAnncDownload
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cfi_data()
    else:
        print '参数输入不正确'
