# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import unicodecsv
import json
import datetime
import time
import scrapy
from scrapy import log
import json
from scrapy.http.request import Request
from annc.items import anncItem
from annc.settings import NEWSPIDER_MODULE
import urllib2
import logging
import logging.handlers
import codecs
from bs4 import BeautifulSoup

################### 读取配置文件 ###########################
# file path config
from annc.settings import ANNC_PATH
from annc.settings import LOG_PATH

#################### 创建目录 ##############################
if os.path.exists(ANNC_PATH) == False:
    os.makedirs(ANNC_PATH)
if os.path.exists(LOG_PATH) == False:
    os.makedirs(LOG_PATH)

# API 地址	
req = "http://www.cninfo.com.cn/cninfo-new/announcement/query"
# 用于id去重
d = dict()

# Spider Class
class anncSpider(scrapy.Spider):
	name = 'annc'

	def __init__(self, annc_type, date_range, *args, **kwargs):
		self.type = annc_type
		self.daterange = date_range

	def start_requests(self):
		global logger_error
		global logger

		if len(self.daterange) == 8:
			start_date = self.daterange[0:8]
			end_date = self.daterange[0:8]
		else:
			start_date = self.daterange[0:8]
			end_date = self.daterange[9:]
		if int(time.strftime('%H', time.localtime(time.time()))) > 14 and end_date == datetime.date.today().strftime("%Y%m%d"):
			end_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y%m%d")

		date_range = []
		# 先变为datetime对象便于操作
		curr_date = datetime.date( int(start_date[0:4]), int(start_date[4:6]), int(start_date[6:8]) )
		end_date = datetime.date( int(end_date[0:4]), int(end_date[4:6]), int(end_date[6:8]) )
		while curr_date != end_date:
			date_range.append(curr_date)
			curr_date += datetime.timedelta(days = 1)
		# 再把最后一天的加上
		date_range.append(curr_date)
		log_record = []
		# 按天去下载
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
					if self.type == 'sse':
						LOG_ERROR_FILE = LOG_PATH + str(datei)[0:7].replace('-', '') + '_error.log'
					# if self.type == 'regulator':
					# 	LOG_ERROR_FILE = LOG_PATH + str(datei)[0:7].replace('-', '') + '_error.log'

					handler_error = logging.handlers.RotatingFileHandler(
						LOG_ERROR_FILE, maxBytes=1024 * 1024, backupCount=5)  # 实例化handler
					fmt_error = '%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s'
					formatter_error = logging.Formatter(fmt_error)  # 实例化formatter
					handler_error.setFormatter(
						formatter_error)      # 为handler添加formatter
					logger_error = logging.getLogger('annc_error')    # 获取名为content的logger
					# 为logger添加handler
					logger_error.addHandler(handler_error)
					logger_error.setLevel(logging.ERROR)

					# INFO日志处理
					if self.type == 'sse':
						LOG_INFO_FILE = LOG_PATH + str(datei)[0:7].replace('-', '') + '_info.log'
					# if annc_type == 'regulator':
					# 	LOG_INFO_FILE = LOG_PATH + str(datei)[0:7].replace('-', '') + '_info.log'

					handler = logging.handlers.RotatingFileHandler(
						LOG_INFO_FILE, maxBytes=1024 * 1024, backupCount=5)  # 实例化handler
					fmt = '%(asctime)s  - %(levelname)s - %(message)s'
					formatter = logging.Formatter(fmt)  # 实例化formatter
					handler.setFormatter(formatter)      # 为handler添加formatter
					logger = logging.getLogger('annc_info')    # 获取名为content的logger
					logger.addHandler(handler)          # 为logger添加handler
					logger.setLevel(logging.INFO)
			#####################################################################################
			yield scrapy.FormRequest( url = req, method = "POST", formdata={'column': self.type, 'seDate': str(datei)[0:10], 'pageNum': '1', 'tabName': 'fulltext'}, callback = lambda response, datei = datei: self.parse(response, datei), dont_filter = True)


	def parse(self, response, datei):
		j = json.loads(response.body_as_unicode())
		totalRecordNum = j['totalRecordNum']
		pageNum = totalRecordNum / 30 + 1 if totalRecordNum % 30 > 0 else totalRecordNum / 30
		for i in range (1, pageNum + 1):
			yield scrapy.FormRequest( url = req, method = "POST", formdata={'column': self.type, 'seDate': str(datei)[0:10], 'pageNum': str(i), 'tabName': 'fulltext'}, callback = lambda response, datei = datei: self.main(response, datei), dont_filter = True)


	def main(self, response, datei):
		j = json.loads(response.body_as_unicode())['announcements']
		for i in range(0, len(j)):
			item = anncItem()
			item['symbol'] = str(j[i]['secCode'])
			if len(item['symbol']) == 6:
				if item['symbol'] in d:
					d[item['symbol']] = int(d[item['symbol']]) + 1
				else:
					d[item['symbol']] = 1
				if d[item['symbol']] < 10:
					anncid = item['symbol'] + str(datei).replace('-', '') + '00' + str(d[item['symbol']])
				elif d[item['symbol']] < 100:
					anncid = item['symbol'] + str(datei).replace('-', '') + '0'  + str(d[item['symbol']])
				else:
					anncid = item['symbol'] + str(datei).replace('-', '')        + str(d[item['symbol']])
				item['annc_Key'] = str(anncid)
				item['title'] = str(j[i]['announcementTitle'].replace(',', '').replace('<font color=red>', '').replace('</font>', '').replace('\n', ''))
				item['source'] = str('http://www.cninfo.com.cn/' + j[i]['adjunctUrl'].strip())
				item['abbr_Name'] = str(j[i]['secName'])
				item['valid'] = 0
				file_type = ""
				if str.lower(item['source']).find('html') > -1:
					file_type = 'TXT'
					if downhtml(item['annc_Key'], item['source']):
						item['valid'] = 1
				elif str.lower(item['source']).find('.js') > -1:
					file_type = 'TXT'
					if downjs(item['annc_Key'], item['source']):
						item['valid'] = 1
				elif str.lower(item['source']).find('.pdf') > -1:
					file_type = 'PDF'
					if downpdf(item['annc_Key'], item['source']):
						item['valid'] = 1
				elif str.lower(item['source']).find('.doc') > -1:
					if str.lower(item['source']).find('.docx') > -1:
						file_type = 'DOCX'
					else:
						file_type = 'DOC'
					if downdoc(item['annc_Key'], item['source']):
						item['valid'] = 1
				else:
					file_type = 'UNKNOWN'
				item['format'] = str(file_type)
				anncTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(j[i]['announcementTime'] / 1000))
				item['annc_Date'] = anncTime[0:10]
				item['annc_Time'] = anncTime[-8:]
				item['acqu_Time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
				yield item


###################################### 功能性函数 下载公告文件 #############################################
# 把html网页的文字下载到txt中
def downhtml(anncid, url):
	flag = False
	try:
		contentpage = urllib2.urlopen(url)
	except urllib2.URLError, e:
		logger_error.error('公告链接错误 id号 URL网址: %s %s %s' % (e, anncid, url))
	except socket.timeout:
		downhtml(anncid, url)
	except socket.error, e:
		if str(e).find('Connection reset by peer') or str(e).find('Operation timed out') != -1:
			downhtml(anncid, url)
		else:
			logger_error.error('公告链接错误 id号 URL网址: %s %s %s' % (e, anncid, url))
	else:
		contentsoup = BeautifulSoup(
			contentpage, 'lxml', from_encoding="utf-8")
		try:
			content = contentsoup.findAll('span', {'class': 'da'})
			con_len = len(content)
			content_txt = content[con_len - 1].get_text()
		except IndexError, e:
			try:
				content = contentsoup.findAll('pre')
				con_len = len(content)
				content_txt = content[0].get_text()
			except IndexError, e:
				logger_error.error('页面解析错误 id号 URL网址: %s %s %s' % (e, anncid, url))
			else:
				f_temp = codecs.open(ANNC_PATH + anncid + '.txt', 'w+', encoding='utf-8')
				f_temp.write(content_txt)
				f_temp.close()
				logger.info('成功下载： id为：%s url：%s ' % (anncid, url))
				flag = True
		else:
			f_temp = codecs.open(ANNC_PATH + anncid + '.txt', 'w+', encoding='utf-8')
			f_temp.write(content_txt)
			f_temp.close()
			logger.info('成功下载： id为：%s url：%s ' % (anncid, url))
			flag = True
	finally:
		if 'contentpage' in locals().keys():
			contentpage.close()
		return flag

# 把js返回的文字下载到txt中
def downjs(anncid, url):
	flag = False
	try:
		contentpage = urllib2.urlopen(url)
		content_txt = contentpage.read()
	except urllib2.URLError, e:
		logger_error.error('公告链接错误 id号 URL网址: %s %s %s' % (e, anncid, url))
	except socket.timeout:
		downjs(anncid, url)
	except socket.error, e:
		if str(e).find('Connection reset by peer') or str(e).find('Operation timed out') != -1:
			downjs(anncid, url)
		else:
			logger_error.error('公告链接错误 id号 URL网址: %s %s %s' % (e, anncid, url))
	else:
		try:
			content_txt = content_txt.decode('gbk').encode('utf-8')
		except UnicodeDecodeError, e:
			logger_error.error('js文件解码错误 id号 URL网址: %s %s %s' % (e, anncid, url))
		else:
			content_txt = re.search(
				r'"Zw":(.*)<br>', content_txt)
			if content_txt == None:
				logger_error.error('js文件解码错误 id号 URL网址: %s %s %s' % (e, anncid, url))
			else:
				content_txt = content_txt.group().replace('<br>', '').replace('"Zw":"', '')
				f_temp = codecs.open(
					ANNC_PATH + anncid + '.txt', 'w+', encoding='utf-8')
				f_temp.write(content_txt)
				f_temp.close()
				logger.info('成功下载： id为：%s url：%s ' % (anncid, url))
				flag = True   
	finally:
		if 'contentpage' in locals().keys():
			contentpage.close()
		return flag
        
# 下载doc
def downdoc(anncid, url):
	flag = False
	try:
		contentpage = urllib2.urlopen(url)
		content_doc = contentpage.read()
	except urllib2.URLError, e:
		logger_error.error('公告链接错误 id号 URL网址: %s %s %s' % (e, anncid, url))
	except urllib2.URLError, e:
		logger_error.error('公告链接错误 id号 URL网址: %s %s %s' % (e, anncid, url))
	except httplib.BadStatusLine, e:
		logger_error.error('公告链接错误 id号 URL网址: %s %s %s' % (e, anncid, url))
	except socket.timeout:
	    downdoc(anncid, url)
	except socket.error, e:
		if str(e).find('Connection reset by peer') or str(e).find('Operation timed out') != -1:
			downdoc(anncid, url)
		else:
			logger_error.error('公告链接错误 id号 URL网址: %s %s %s' % (e, anncid, url))
	else:
		if url.find('.docx') > -1 or url.find('.DOCX') > -1:
			f_temp = open(ANNC_PATH + anncid + '.docx', 'w+')
		else:
			f_temp = open(ANNC_PATH + anncid + '.doc', 'w+')
		f_temp.write(content_doc)
		f_temp.close()
		logger.info('成功下载： id为：%s url：%s ' % (anncid, url))
		flag =True
	finally:    
		if 'contentpage' in locals().keys():
			contentpage.close()
		return flag

# 下载pdf
def downpdf(anncid, url):
	flag = False
	try:
		contentpage = urllib2.urlopen(url)
		content_pdf = contentpage.read()
	except httplib.BadStatusLine, e:
		logger_error.error('公告链接错误 id号 URL网址: %s %s %s' % (e, anncid, url))
	except socket.timeout:
		downpdf(anncid, url)
	except socket.error, e:
		if str(e).find('Connection reset by peer') or str(e).find('Operation timed out') != -1:
			downpdf(anncid, url)
		else:
			logger_error.error('公告链接错误 id号 URL网址: %s %s %s' % (e, anncid, url))
	else:
		f_temp = open(ANNC_PATH + anncid + '.pdf', 'w+')
		f_temp.write(content_pdf)
		f_temp.close()
		logger.info('成功下载： id为：%s url：%s ' % (anncid, url))
		flag = True
	finally:
		if 'contentpage' in locals().keys():
			contentpage.close()
		return flag