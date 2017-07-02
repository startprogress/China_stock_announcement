-- 创建数据库
CREATE DATABASE IF NOT EXISTS stock CHARACTER SET utf8 COLLATE utf8_general_ci;;
USE stock;
-- 监管公告的数据表
CREATE TABLE `csrc_annc_list` (
  `Annc_Key` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Symbol` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Regu_Type` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Title` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Annc_Date` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Annc_Time` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Format` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Source` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Valid` tinyint(1) DEFAULT NULL,
  `Acqu_Time` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- 上市公司的数据表
CREATE TABLE `sse_annc_list` (
  `Annc_Key` char(17) COLLATE utf8_bin DEFAULT NULL,
  `Symbol` char(6) COLLATE utf8_bin DEFAULT NULL,
  `Abbr_Name` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Title` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Annc_Date` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Annc_Time` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Format` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Source` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Valid` tinyint(1) DEFAULT NULL,
  `Acqu_Time` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- 监管公告涉及列表的数据表
CREATE TABLE `csrc_impact_list` (
  `Annc_Key` varchar(255) COLLATE utf8_bin DEFAULT '',
  `Symbol` varchar(255) COLLATE utf8_bin DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- 监管类型的数据表
CREATE TABLE `regu_type_info` (
  `Abbv_EN` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Abbv_CN` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Full_Name_EN` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Full_Name_CN` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Source` varchar(255) COLLATE utf8_bin DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
-- 将码表数据插入
Insert into regu_type_info
(Abbv_EN,Abbv_CN,Full_Name_EN,Full_Name_CN,Source)
values
("sse","上交所","Shanghai Stock Exchange","上海证券交易所","http://www.sse.com.cn"),
("szse","深交所","Shenzhen Stock Exchange","深圳证券交易所","http://www.szse.cn"),
("csrc","证监会","China Securities Regulatory Commission","中国证券监督管理委员会","http://www.csrc.gov.cn"),
("csdc","中证登","China Securities Registration and Clearing China securities registration and Clearing China securities registration and Clearing Corporation","中国证券登记结算有限公司","http://www.chinaclear.cn");