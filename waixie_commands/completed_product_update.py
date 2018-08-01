# -*- coding: utf-8 -*-

import datetime
import time
import sys

from util.util import *
import config

reload(sys)
sys.setdefaultencoding('utf8')


def excute_form_source_db(root_category):
    """下架产品更新
        源数据搜索条件：ebay_product数据库  listing_status:Completed  and   update_date为今天
        目标数据：waixie_new数据库 source表 status更新为3
    """
    source_sql = """
        select item_id
        from ebay_product_info_{category} 
        WHERE listing_status = 'Completed' AND to_days(update_date) = to_days(now())
    """.format(category=root_category)

    s_time = datetime.datetime.now()
    datas = source_db_manger.execute_sql_query(source_sql)
    e_time = datetime.datetime.now()
    print '源数据查询耗时：',e_time - s_time

    data_list = []
    for data in datas:
        item_id = data.get('item_id', '')
        if item_id:
            data_list.append(item_id)

    update_sql = """
            update waixie_product_source_{category} 
            set status = 3,update_date = '{source_update_date}',update_user = 0
            WHERE item_id IN ({item_list})
        """.format(category=root_category,
                   source_update_date=datetime.datetime.now(tz=utc_tz).strftime('%Y-%m-%d %H:%M:%S'),
                   item_list="','".join(data_list))

    s_time1 = datetime.datetime.now()
    waixie_db_manger.execute_sql_cud(update_sql)
    e_time1 = datetime.datetime.now()
    print 'waixie source表数据更新耗时：', e_time1 - s_time1

    ##################################
    # 外协上架产品信息下架更新
    update_amazon_base_sql = """
        update waixie_amazon_product_base 
        set status = 4,update_date = '{base_update_date}',update_user = 0 
        WHERE item_id IN ({item_list})
    """.format(base_update_date=datetime.datetime.now(tz=utc_tz).strftime('%Y-%m-%d %H:%M:%S'),
               item_list="','".join(data_list))

    s_time2 = datetime.datetime.now()
    waixie_db_manger.execute_sql_cud(update_amazon_base_sql)
    e_time2 = datetime.datetime.now()
    print 'waixie amazon base表数据更新耗时：', e_time2 - s_time2

    update_amazon_detail_sql = """
            update waixie_amazon_product_detail 
            set status = 4,update_date = '{detail_update_date}',update_user = 0 
            WHERE item_id IN ({item_list})
        """.format(detail_update_date=datetime.datetime.now(tz=utc_tz).strftime('%Y-%m-%d %H:%M:%S'),
                   item_list="','".join(data_list))

    s_time3 = datetime.datetime.now()
    waixie_db_manger.execute_sql_cud(update_amazon_detail_sql)
    e_time3 = datetime.datetime.now()
    print 'waixie amazon detail表数据更新耗时：', e_time3 - s_time3

    #################################


def main_threads():
    for root_category in config.ROOT_CATEGORY:
        print '==========source表 品类ID：', root_category, '下架产品更新start=========='
        excute_form_source_db(root_category)
        print '==========source表 品类ID：', root_category, '下架产品更新end=========='


if __name__ == "__main__":
    start = datetime.datetime.now()
    print "start",start.strftime('%Y-%m-%d %H:%M:%S')
    main_threads()
    end = datetime.datetime.now()
    print "end", end.strftime('%Y-%m-%d %H:%M:%S')
    print "终于u结束了呀", end-start

