# -*- coding: utf-8 -*-

import datetime
import sys

from util.util import *
import config

reload(sys)
sys.setdefaultencoding('utf8')


def conversion_waixie(datas):
    """
    将原数据结构转换为waixie临时存储数据表所需数据结构
    {root_category1:[...],root_category2:[...]...}
    """

    waixie_datas_dict = {}
    waixie_child_datas_dict = {}

    for data in datas:
        waixie_datas_item = []
        item_id = data.get('item_id')
        root_category = data.get('root_category_id')
        price = data.get('counverted_current_price')
        quantity = data.get('quantity')
        quantity_sold = data.get('quantity_sold')
        variations = data.get('variations')

        if not item_id:
            continue

        waixie_datas_item.append(item_id)
        waixie_datas_item.append(price)
        waixie_datas_item.append(quantity)
        waixie_datas_item.append(quantity_sold)
        waixie_datas_item.append(datetime.datetime.now(tz=utc_tz).strftime('%Y-%m-%d %H:%M:%S'))

        values1 = target_table_values_map(waixie_datas_item)

        if root_category in waixie_datas_dict:
            waixie_datas_dict[root_category].append(values1)
        else:
            waixie_datas_dict[root_category] = []

        try:
            childs = json.loads(variations)
        except:
            print "你这孩子节点有错误得呀。"
            childs = []

        for child in childs:
            child_item = []
            sku = child.get('sku')
            price = child.get('price')
            quantity = child.get('quantity')
            quantity_sold = child.get('quantity_sold')

            if not sku:
                continue

            child_item.append(item_id)
            child_item.append(sku)
            child_item.append(price)
            child_item.append(quantity)
            child_item.append(quantity_sold)
            child_item.append(datetime.datetime.now(tz=utc_tz).strftime('%Y-%m-%d %H:%M:%S'))

            values2 = target_table_values_map(child_item)

            if root_category in waixie_child_datas_dict:
                waixie_child_datas_dict[root_category].append(values2)
            else:
                waixie_child_datas_dict[root_category] = []

    return waixie_datas_dict,waixie_child_datas_dict


def excute_form_source_db():
    """价格变化更新
        源数据：ebay_product数据库  ebay_product_num_change表
        查询出父子产品的价格/库存/销量

        目标数据：waixie_new库  新建临时表 waixie_product_num_change_categoryID， waixie_product_child_num_change_categoryID
        将源数据父子产品分别更新到waixie对应临时表中
    """

    source_sql = """
                select item_id,root_category_id,counverted_current_price,quantity,quantity_sold,variations
                from ebay_product_num_change 
            """

    s_time = datetime.datetime.now()
    datas = source_db_manger.execute_sql_query(source_sql)
    e_time = datetime.datetime.now()
    print '源数据查询耗时：',e_time - s_time

    waixie_datas_dict,waixie_child_datas_dict = conversion_waixie(datas)

    for root_category in waixie_datas_dict:
        source_tmp_table_name = config.waixie_source_temp_table_name.format(root_category=root_category)
        waixie_db_manger.create_table_or_not(source_tmp_table_name, config.create_temp_table_map.get('source').format(table_name=source_tmp_table_name))

        insert_values = ",".join(waixie_datas_dict[root_category])

        sql = "REPLACE INTO {tableName} ({fields}) values ".format(tableName=source_tmp_table_name,
                                                                   fields=','.join(config.SOURCE_TEMP_FIELD)) + insert_values
        s_time1 = datetime.datetime.now()
        waixie_db_manger.execute_sql_cud(sql)
        e_time1 = datetime.datetime.now()
        print 'source临时表 品类ID：', root_category,'数据插入耗时：', e_time1 - s_time1

        update_sql = """
            update waixie_product_source_{root_category} src join {tableName} temp 
            on src.item_id = temp.item_id 
            set src.old_price = src.price,src.price = temp.price,src.quantity = temp.quantity,src.sales = temp.quantity_sold,
                src.update_date = '{source_update_date}',src.update_user = 0 
            WHERE DATE(temp.update_date) = '{temp_update_date}'
        """.format(root_category=root_category,
                   tableName=source_tmp_table_name,
                   source_update_date=datetime.datetime.now(tz=utc_tz).strftime('%Y-%m-%d %H:%M:%S'),
                   temp_update_date=datetime.datetime.now(tz=utc_tz).strftime('%Y-%m-%d'))

        s_time2 = datetime.datetime.now()
        waixie_db_manger.execute_sql_cud(update_sql)
        e_time2 = datetime.datetime.now()
        print 'source表 品类ID：', root_category, '数据更新耗时：', e_time2 - s_time2

    for root_category in waixie_child_datas_dict:
        child_tmp_table_name = config.waixie_child_temp_table_name.format(root_category=root_category)
        waixie_db_manger.create_table_or_not(child_tmp_table_name,config.create_temp_table_map.get('child').format(table_name=child_tmp_table_name))

        insert_values = ",".join(waixie_child_datas_dict[root_category])

        child_sql = "REPLACE INTO {tableName} ({fields}) values ".format(tableName=child_tmp_table_name,
                                                                         fields=','.join(config.CHILD_TEMP_FIELD)) + insert_values
        s_time3 = datetime.datetime.now()
        waixie_db_manger.execute_sql_cud(child_sql)
        e_time3 = datetime.datetime.now()
        print 'child临时表 品类ID：', root_category, '数据插入耗时：', e_time3 - s_time3

        update_child_sql = """
                    update waixie_product_child_{root_category} child join {tableName} temp 
                    on child.item_id = temp.item_id AND child.sku = temp.sku
                    set child.old_price = child.price,child.price = temp.price,child.quantity = temp.quantity,child.sales = temp.quantity_sold,
                        child.update_date = '{child_update_date}',child.update_user = 0 
                    WHERE DATE(temp.update_date) = '{temp_update_date}'
                """.format(root_category=root_category,
                           tableName=child_tmp_table_name,
                           child_update_date=datetime.datetime.now(tz=utc_tz).strftime('%Y-%m-%d %H:%M:%S'),
                           temp_update_date=datetime.datetime.now(tz=utc_tz).strftime('%Y-%m-%d'))

        s_time4 = datetime.datetime.now()
        waixie_db_manger.execute_sql_cud(update_child_sql)
        e_time4 = datetime.datetime.now()
        print 'child表 品类ID：', root_category, '数据更新耗时：', e_time4 - s_time4

        #################################
        # 外协上架产品信息价格更新
        update_amazon_detail_sql = """
            update waixie_amazon_product_detail detail 
            join {tableName} temp on detail.item_id = temp.item_id AND detail.sku = temp.sku 
            join waixie_product_child_{root_category} child on child.item_id = temp.item_id AND child.sku = temp.sku 
            set detail.new_price = detail.standard_price * temp.price / child.old_price,
                detail.update_date = '{detail_update_date}',detail.update_user = 0 
        """.format(tableName=child_tmp_table_name,
                   root_category=root_category,
                   detail_update_date=datetime.datetime.now(tz=utc_tz).strftime('%Y-%m-%d %H:%M:%S'))

        s_time5 = datetime.datetime.now()
        waixie_db_manger.execute_sql_cud(update_amazon_detail_sql)
        e_time5 = datetime.datetime.now()
        print 'waixie amazon detail 表 数据更新耗时：', e_time5 - s_time5

        #################################


if __name__ == "__main__":
    start = datetime.datetime.now()
    print "start",start.strftime('%Y-%m-%d %H:%M:%S')

    excute_form_source_db()

    end = datetime.datetime.now()
    print "end", end.strftime('%Y-%m-%d %H:%M:%S')
    print "终于u结束了呀", end-start

