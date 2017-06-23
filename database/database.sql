 # 创建数据库;
CREATE DATABASE stock CHARACTER SET utf8 COLLATE utf8_general_ci;;
USE stock;
 # 监管公告的数据表
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

#上市公司的数据表
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

#监管公告涉及列表的数据表
CREATE TABLE `csrc_impact_list` (
  `Annc_Key` varchar(255) COLLATE utf8_bin DEFAULT '',
  `Symbol` varchar(255) COLLATE utf8_bin DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

#监管类型的数据表
CREATE TABLE `regu_type_info` (
  `Abbv_EN` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Abbv_CN` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Full_Name_EN` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Full_Name_CN` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `Source` varchar(255) COLLATE utf8_bin DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
