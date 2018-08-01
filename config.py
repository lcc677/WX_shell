# -*- coding: utf-8 -*-
# Created by cc on 18-7-14.
import re

REDIS = {
    'host': '127.0.0.1',
    'port': 6379
}

ROOT_CATEGORY = [
    '14339',
    # '293', '15032', '58058', '625', '2984', '1281', '1249',
    # '99', '20081', '11700', '220',
    # '888', '12576', '26395',
    # '281', '550',   '1', '14339', '619',
    # '11450',
    # '6000',
]
SOURCE_DB = {
    'host': '192.168.3.121',
    'user': 'root',
    'password': 'x',
    'db': 'ebay_product',
    'port': 3306
}

WAIXIE_DB = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'x',
    'db': 'waixie_new',
    'port': 3306
}

# 源数据库查询的字段
SOURCE_FIELD = [
    'item_id','listing_status','primary_category_id','primary_category_id_path','primary_category_name','title','brand','description',
    'gallery_url','picture_url','attr_info','convert_current_price','quantity','quantity_sold','ship_price','seller','location','ship_to_locations'
    'exclude_ship_to_location','handling_time',
    'start_time','end_time','variations',
]

# 外协数据库 主表字段
WAIXIE_FIELD = [
    'item_id','category_id','category_id_path','category_name','title','brand',
    'main_image','attr_info','price','quantity',
    'sales','ship_price','seller','location',
    'start_time','end_time','time_send','update_date','create_date'
]

# 外协数据库 子表数据
WAIXIE_CHILD_FIELD = [
    'item_id','sku','main_image','attribute','images','price','quantity','sales'
]

# 外协数据库 描述信息表数据
WAIXIE_DESC_FIELD = [
    'item_id','described','feature','images','ship_to_location','exclude_ship_to_location','update_date','create_date'
]

# 更新的数据长度
LENGTH = 20000

# ebay图片需要替换成大图的固定URL
BIG_IMG_URL = 'https://i.ebayimg.com/images/g/{img}/s-l1600.jpg'

# 头像字符传的取值范围的正则
EMOJI_RE = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
EMOJI_RE2 = re.compile(u'[\U00010000-\U0010ffff]')

SOURCE_TABLE_NAME = 'waixie_product_source_{root_category}'
DESC_TABLE_NAME = 'waixie_product_description_{root_category}'
CHILD_TABLE_NAME = 'waixie_product_child_{root_category}'

CREATE_TABLE_MAP_NEW = {
    "source":"""
    CREATE TABLE `{table_name}` (
      `id` int(11) NOT NULL AUTO_INCREMENT ,
      `item_id` varchar(45) NOT NULL COMMENT '产品ID',
      `category_id` varchar(45) NOT NULL COMMENT '品类ID',
      `category_id_path` varchar(100) NOT NULL COMMENT '品类ID路径',
      `category_name` varchar(150) NOT NULL COMMENT '品类名称',
      `title` varchar(125) DEFAULT '' COMMENT '标题',
      `brand` varchar(100) DEFAULT '' COMMENT '品牌',
      `main_image` varchar(200) DEFAULT '' COMMENT '主图',
      `attr_info` varchar(200) DEFAULT '' COMMENT '属性列表',
      `price` float DEFAULT '0.0' COMMENT '价格',
      `old_price` float DEFAULT '0.0' COMMENT '上次更新的价格',
      `quantity` int(11) DEFAULT '0' COMMENT '库存',
      `sales` int(11) DEFAULT '0' COMMENT '销量',
      `ship_price` float DEFAULT '0.0' COMMENT '运费',
      `seller` VARCHAR(200) COMMENT '卖家',
      `location` varchar(50) DEFAULT '' COMMENT '卖家所在的地方',
      `start_time` datetime NOT NULL COMMENT '上架时间',
      `end_time` datetime NOT NULL COMMENT '下架时间',
      `country` tinyint(11) DEFAULT '1' COMMENT '1:国内，2:国外，默认是1国内',
      `time_send` varchar(30) DEFAULT '' COMMENT '时效',
      `status` tinyint(11) DEFAULT '0' COMMENT '0:未审核 1:未上架 2:问题产品 3:已上架',
      `remark` varchar(225) DEFAULT '' COMMENT '问题产品的问题原因',
      `sign_type` tinyint(11) DEFAULT '0' COMMENT '标记方式，1：手动，2：自动，0：不是问题产品',
      `update_date` datetime DEFAULT NULL COMMENT '更新时间',
      `update_user` int(11) DEFAULT '0' COMMENT '修改人',
      `create_date` datetime DEFAULT NULL COMMENT '插入时间',
      PRIMARY KEY (`id`),
      UNIQUE KEY `item_id_index` (`item_id`),
      KEY `category_id_path_index` (`category_id_path`),
      KEY `sales_index` (`sales`),
      KEY `price_index` (`price`),
      KEY `sign_type_index` (`sign_type`),
      KEY `brand_index` (`brand`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='外协主产品信息';
    """,
    "child":"""
      CREATE TABLE `{table_name}` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `item_id` varchar(45) NOT NULL COMMENT '产品ID',
      `sku` varchar(100) NOT NULL COMMENT '产品SKU',
      `main_image` varchar(200) DEFAULT '' COMMENT '主图',
      `attribute` varchar(300) DEFAULT '' COMMENT '属性',
      `images` text COMMENT '图片列表',
      `price` float DEFAULT '0.0' COMMENT '价格',
      `old_price` float DEFAULT '0.0' COMMENT '上次更新的价格',
      `quantity` int(11) DEFAULT '0' COMMENT '库存',
      `sales` int(11) DEFAULT '0' COMMENT '销量',
      PRIMARY KEY (`id`),
      KEY `item_id_index` (`item_id`),
      UNIQUE KEY `union_unique_index` (`item_id`,`sku`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='ebay产品变体';
    """,
    "description":"""
      CREATE TABLE `{table_name}` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `item_id` varchar(45) NOT NULL COMMENT '产品ID',
      `described` text,
      `feature` text,
      `images` text,
      `ship_to_location` text,
      `exclude_ship_to_location` text,
      `update_date` datetime DEFAULT NULL COMMENT '更新时间',
      `update_user` int(11) DEFAULT '0' COMMENT '修改人',
      `create_date` datetime DEFAULT NULL COMMENT '插入时间',
      PRIMARY KEY (`id`),
      UNIQUE KEY `item_id_index` (`item_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

    """
}

# 价格更新 临时数据表相关信息
waixie_source_temp_table_name = 'waixie_product_num_change_{root_category}'
waixie_child_temp_table_name = 'waixie_product_child_num_change_{root_category}'

SOURCE_TEMP_FIELD = [
    'item_id','price','quantity','quantity_sold','update_date'
]

CHILD_TEMP_FIELD = [
    'item_id','sku','price','quantity','quantity_sold','update_date'
]

create_temp_table_map = {
    'source':"""
    CREATE TABLE `{table_name}` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `item_id` varchar(45) NOT NULL COMMENT '产品ID',
  `price` float DEFAULT 0 COMMENT '价格',
  `quantity` int(11) DEFAULT 0 COMMENT '库存',
  `quantity_sold` int(11) DEFAULT 0 COMMENT '销量',
  `update_date` datetime DEFAULT NULL COMMENT '更新日期',
  PRIMARY KEY (`id`),
  UNIQUE KEY `item_id_unique_index` (`item_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
    """,
    'child':"""
    CREATE TABLE `{table_name}` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `item_id` varchar(45) NOT NULL COMMENT '产品ID',
  `sku` varchar(100) NOT NULL COMMENT '产品sku',
  `price` float DEFAULT 0 COMMENT '价格',
  `quantity` int(11) DEFAULT 0 COMMENT '库存',
  `quantity_sold` int(11) DEFAULT 0 COMMENT '销量',
  `update_date` datetime DEFAULT NULL COMMENT '更新日期',
  PRIMARY KEY (`id`),
  UNIQUE KEY `item_id_sku_unique_index` (`item_id`,`sku`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
    """
}


