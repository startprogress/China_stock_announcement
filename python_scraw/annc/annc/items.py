# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class anncItem(scrapy.Item):
	annc_Key = scrapy.Field()
	symbol = scrapy.Field()
	abbr_Name = scrapy.Field()
	title = scrapy.Field()
	annc_Date = scrapy.Field()
	annc_Time = scrapy.Field()
	format = scrapy.Field()
	source = scrapy.Field()
	valid = scrapy.Field()
	acqu_Time = scrapy.Field()