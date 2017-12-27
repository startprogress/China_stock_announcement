# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi

class AnncPipeline(object):

	def __init__(self, dbpool):
		self.dbpool = dbpool

	# database config
	@classmethod
	def from_settings(cls, settings):
		dbparams = dict(
			host = settings['HOST_ADDRESS'],  
			db = settings['DB_NAME'],
			user = settings['USER'],
			passwd = settings['PASSWORD'],
			charset = 'utf8',  # 编码要加上，否则可能出现中文乱码问题
			cursorclass = MySQLdb.cursors.DictCursor,
			use_unicode = False,
		)
		dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)  # **表示将字典扩展为关键字参数,相当于host=xxx,db=yyy....
		return cls(dbpool)  # 相当于dbpool付给了这个类，self中可以得到

	# pipeline默认调用
	def process_item(self, item, spider):
		query = self.dbpool.runInteraction(self._conditional_insert, item)  # 调用插入的方法
		query.addErrback(self._handle_error, item, spider)  # 调用异常处理方法

    # 写入数据库中
    # SQL语句在这里
	def _conditional_insert(self, tx, item):
		sql = "insert into sse_annc_list(Annc_Key, Symbol, Abbr_Name, Title, Annc_Date, Annc_Time, Format, Source, Acqu_Time) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
		params = (item['annc_Key'], item['symbol'], item['abbr_Name'], item['title'], item['annc_Date'], item['annc_Time'], item['format'], item['source'], item['acqu_Time'])
		tx.execute(sql, params)

	# 错误处理方法
	def _handle_error(self, failue, item, spider):
		print failue