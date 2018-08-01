# -*- coding: utf-8 -*-
# Created by cc on 18-7-18.
import hashlib
import json
import re
import MySQLdb
import redis
from pytz import timezone
from database_util import UtilsMySQL
from waixie_db_manage import config

utc_tz = timezone('UTC')

r = redis.Redis(host=config.REDIS['host'],port=config.REDIS['port'])
source_db_manger = UtilsMySQL(config.SOURCE_DB)
waixie_db_manger = UtilsMySQL(config.WAIXIE_DB)


def md5(str_info):
    m = hashlib.md5()
    m.update(str_info)
    return m.hexdigest()


def change_pictures(images):
    """修改图片，增大像素,list"""
    change_images = []
    if images:
        if isinstance(images,basestring):
            try:
                images = json.loads(images)
            except:
                images=[]
        for image in images:
            change_images.append(change_picture(image))
    return change_images


def change_picture(image):
    """修改图片，增大像素,单个图片链接"""
    try:
        if image:
            if image.startswith('https://i.ebayimg.com'):
                image_code = image.split('/')[-2]
                return config.BIG_IMG_URL.format(img=image_code)
            else:
                return image
        else:
            return ''
    except:
        return ''


def get_danger_word(filter_sql=None):
    """
    获取危险词
    :return:
    """
    sql = """
    select danger_word from waixie_sensitive_word where status=1
        """
    if filter_sql:
        sql += " and filter_mark = {filter_sql}".format(filter_sql=filter_sql)

    danger_word = waixie_db_manger.execute_sql_query(sql)
    return danger_word


def check_title(title,danger_word):
    """检查标题"""
    if not title:
        return False
    for word in danger_word:
        if not word.get('danger_word'):
            continue
        if word.get('danger_word').lower() in title.lower():
            return True
    return False


def format_emoticon(temp_str, res_str=''):
    """
    替换字符串中的表情，返回格式化后的字符串
    在title和seller字段中可能出现表情
    :param temp_str:待转化的字符串
    :param res_str:替换成的字符串
    :return:
    """
    str = re.sub(config.EMOJI_RE,res_str,temp_str)
    str2 = re.sub(config.EMOJI_RE2,res_str,str)
    return str2


def target_table_values_map(data_list):
    """
    转换为数据插入sql中  values部分
    :param data_list: list
    :return: (value1,value2...)
    """
    # 全部转变成str类型
    string = map(unicode, data_list)
    string = map(format_emoticon,string)
    values = "('" + "','".join(map(MySQLdb.escape_string, string)) + "')"
    return values


def select_waixie_tables(reg=None):
    """
    获取外协库符合要求的表
    :param reg: 正则表达式
    :return: list [...]
    """
    sql = "select table_name from information_schema.tables where table_schema='waixie_new' and table_name regexp '{reg}';".format(reg=reg)
    datas = waixie_db_manger.execute_sql_query(sql)
    results = []
    for data in datas:
        table_name = data.get('table_name')
        if table_name:
            results.append(table_name)
    return results












