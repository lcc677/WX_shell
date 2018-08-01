# -*- coding: utf-8 -*-

import datetime
import time
import sys

from util.util import *
import config

reload(sys)
sys.setdefaultencoding('utf8')

danger_word = get_danger_word()
def conversion_waixie(datas):
    """
    将原数据结构转换为waixie表所需数据结构
    """
    waixie_datas = []
    waixie_desc_datas = []
    waixie_child_datas = []
    for data in datas:
        waixie_datas_item = []
        waixie_desc_datas_item = []
        item_id = data.get('item_id','')
        title = data.get('title')
        gallery_url = data.get('gallery_url')  # 主图
        picture_url = data.get('picture_url')
        images = change_pictures(picture_url)  # 产品图片列表

        variation = data.get('variations')
        if check_title(title,danger_word):
            print "=====qinquan====="
            continue
        if not item_id:
            continue

        # =======waixie source start=======
        waixie_datas_item.append(item_id)
        waixie_datas_item.append(data.get('primary_category_id'))
        waixie_datas_item.append(data.get('primary_category_id_path'))
        waixie_datas_item.append(data.get('primary_category_name'))
        waixie_datas_item.append(format_emoticon(title))
        waixie_datas_item.append(data.get('brand'))
        waixie_datas_item.append(change_picture(gallery_url))
        waixie_datas_item.append(data.get('attr_info'))
        waixie_datas_item.append(data.get('convert_current_price'))
        waixie_datas_item.append(data.get('quantity'))
        waixie_datas_item.append(data.get('quantity_sold'))
        waixie_datas_item.append(data.get('ship_price'))
        waixie_datas_item.append(data.get('seller'))
        waixie_datas_item.append(data.get('location'))
        waixie_datas_item.append(data.get('start_time'))
        waixie_datas_item.append(data.get('end_time'))
        waixie_datas_item.append(data.get('handling_time'))
        waixie_datas_item.append(datetime.datetime.now(tz=utc_tz).strftime('%Y-%m-%d %H:%M:%S'))
        waixie_datas_item.append(datetime.datetime.now(tz=utc_tz).strftime('%Y-%m-%d %H:%M:%S'))

        values1 = target_table_values_map(waixie_datas_item)
        waixie_datas.append(values1)
        # =======waixie source end=======

        # =======waixie description start=======
        waixie_desc_datas_item.append(item_id)
        waixie_desc_datas_item.append('')
        waixie_desc_datas_item.append('')
        waixie_desc_datas_item.append(json.dumps(images) if images else '')
        waixie_desc_datas_item.append(data.get('ship_to_locations'))
        waixie_desc_datas_item.append(data.get('exclude_ship_to_location'))
        waixie_desc_datas_item.append(datetime.datetime.now(tz=utc_tz).strftime('%Y-%m-%d %H:%M:%S'))
        waixie_desc_datas_item.append(datetime.datetime.now(tz=utc_tz).strftime('%Y-%m-%d %H:%M:%S'))

        values2 = target_table_values_map(waixie_desc_datas_item)
        waixie_desc_datas.append(values2)
        # =======waixie description end=======

        # =======waixie child start=======
        childs = []
        if variation:
            try:
                childs = json.loads(variation)
            except:
                print "你这孩子节点有错误得呀。"

        for child in childs:
            child_item = []
            sku = child.get('sku')
            pictures = child.get('picture')
            attributes = child.get('attributes')
            price = child.get('price')
            quantity = child.get('quantity')
            sold = child.get('sold')

            # 属性判断是否为空
            attributes = json.dumps(attributes) if attributes else ''
            # sku判断是否为空
            if not sku:
                if attributes:
                    code = md5(str(attributes))
                else:
                    time_long = time.time()
                    code = md5(str(int(round(time_long * 100000))))
                sku = 'our' + code[12:-12]
            # 主图判断是否为空
            main_image = pictures[0] if pictures else ''
            # 图片判断是否为空
            pictures = json.dumps(pictures) if pictures else ''
            child_item.append(item_id)
            child_item.append(sku)
            child_item.append(main_image)
            child_item.append(attributes)
            child_item.append(pictures)
            child_item.append(price)
            child_item.append(quantity)
            child_item.append(sold)

            values3 = target_table_values_map(child_item)
            waixie_child_datas.append(values3)
        # =======waixie child end=======
    return waixie_datas,waixie_desc_datas,waixie_child_datas


def excute_form_source_db(root_category):
    """新品插入操作  将原数据插入到目标数据库相应表中
        原表数据：ebay_product数据库 ebay_product_info_{category_id}表数据
        目标数据：waixie_new数据库 source/child/description表数据
    """
    source_sql = """
        select item_id,
        primary_category_id,
        primary_category_id_path,
        primary_category_name,
        title,
        brand,
        gallery_url,
        picture_url,
        attr_info,
        convert_current_price,
        quantity,
        quantity_sold,
        ship_price,
        seller,
        location,
        ship_to_locations,
        exclude_ship_to_location,
        handling_time,
        start_time,
        end_time,
        variations 
        from ebay_product_info_{category} 
        WHERE listing_status = 'Active' AND to_days(create_date) = to_days(now())
    """.format(category=root_category)

    s_time = datetime.datetime.now()
    datas = source_db_manger.execute_sql_query(source_sql)
    e_time = datetime.datetime.now()
    print '源数据查询耗时：',e_time - s_time

    waixie_datas, waixie_desc_datas, waixie_child_datas = conversion_waixie(datas)

    if waixie_datas:
        insert_values = ",".join(waixie_datas)

        sql = "insert IGNORE into waixie_product_source_{category} ({fields}) values ".format(category=root_category,
                                                                                              fields=','.join(config.WAIXIE_FIELD)
                                                                                              ) + insert_values
        s_time1 = datetime.datetime.now()
        waixie_db_manger.execute_sql_cud(sql)
        e_time1 = datetime.datetime.now()
        print 'waixie source表数据插入耗时：',e_time1 - s_time1

    if waixie_desc_datas:
        insert_desc_values = ",".join(waixie_desc_datas)

        desc_sql = "insert IGNORE into waixie_product_description_{category} ({fields}) values ".format(category=root_category,
                                                                                                        fields=','.join(config.WAIXIE_DESC_FIELD)
                                                                                                        ) + insert_desc_values
        s_time2 = datetime.datetime.now()
        waixie_db_manger.execute_sql_cud(desc_sql)
        e_time2 = datetime.datetime.now()
        print 'waixie description表数据插入耗时：', e_time2 - s_time2

    if waixie_child_datas:
        insert_child_values = ",".join(waixie_child_datas)

        child_sql = "insert IGNORE into waixie_product_child_{category} ({fields}) values ".format(category=root_category,
                                                                                                   fields=','.join(config.WAIXIE_CHILD_FIELD)
                                                                                                   ) + insert_child_values
        s_time3 = datetime.datetime.now()
        waixie_db_manger.execute_sql_cud(child_sql)
        e_time3 = datetime.datetime.now()
        print 'waixie child表数据插入耗时：', e_time3 - s_time3


def main_threads():
    for root_category in config.ROOT_CATEGORY:
        print '==========source/desc/child表 品类ID：', root_category, '新品插入操作start=========='
        excute_form_source_db(root_category)
        print '==========source/desc/child表 品类ID：', root_category, '新品插入操作end=========='


if __name__ == "__main__":
    start = datetime.datetime.now()
    print "start",start.strftime('%Y-%m-%d %H:%M:%S')
    main_threads()
    end = datetime.datetime.now()
    print "end", end.strftime('%Y-%m-%d %H:%M:%S')
    print "终于u结束了呀", end-start

