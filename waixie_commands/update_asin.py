# -*- coding: utf-8 -*-

import datetime
import time
import sys
sys.path.append('..')
from util.util import *
import config
reload(sys)
sys.setdefaultencoding('utf8')

def get_item_sku():
    sql = "select item_sku,account_id,waixie_amazon_product_detail"


# 根据sku获取ASIN
def get_asin_by_sku():
    store_itemsku_map = {}
    return_info = {}
    infos = WaixieAmazonProductDetail.objects.filter(asin='',status=3,account_id="119").values('item_sku','account_id')
    for item_info in infos:
        item_sku_list = store_itemsku_map.get(item_info.get('account_id'),[])
        item_sku_list.append(item_info.get('item_sku'))
        store_itemsku_map.update({
            item_info.get('account_id'):item_sku_list
        })

    for store_key in store_itemsku_map:
        item_skus = store_itemsku_map.get(store_key)
        account = AmazonAccount.objects.get(pk=store_key)
        res = Amazon_xml_WMS(account)
        p = res.create_api('Products')


        length = len(item_skus)
        print account.name,"未更新的产品个数是",length
        request_seller_sku = [item_skus[start:start+3] for start in range(0,length,3)]
        for item in request_seller_sku:
            time.sleep(10)
            try:
                pp = p.get_matching_product_for_id(account.mkplaceid.encode('utf-8'), 'SellerSKU',
                                           item)
                WaixieAmazonProductDetail.objects.filter(item_sku__in=item).update(asin='1')
                result = pp.parsed
                for asin_result in result:
                    if result.get('Error'):
                        print "获取失败了"
                        continue
                    else:
                        asin = result['Products']['Product']['Identifiers']['MarketplaceASIN']['ASIN']['value']

                return_info.append()
            except Exception,e:
                print str(e)
                pass
def main_threads(root_category):
    tablename_source = config.SOURCE_TABLE_NAME.format(root_category=root_category)
    tablename_desc = config.DESC_TABLE_NAME.format(root_category=root_category)
    tablename_child = config.CHILD_TABLE_NAME.format(root_category=root_category)

    waixie_db_manger.create_table_or_not(tablename_source,config.CREATE_TABLE_MAP_NEW.get('source').format(table_name=tablename_source))
    waixie_db_manger.create_table_or_not(tablename_desc, config.CREATE_TABLE_MAP_NEW.get('description').format(table_name=tablename_desc))
    waixie_db_manger.create_table_or_not(tablename_child, config.CREATE_TABLE_MAP_NEW.get('child').format(table_name=tablename_child))

    start1 = datetime.datetime.now()
    print "查询时间",start1.strftime('%Y-%m-%D %H:%M:%S')
    sql = "select count(id) as count from ebay_product_info_{category}".format(category=root_category)
    count = source_db_manger.execute_sql_query(sql)
    if not count:
        print "你竟然连条数都查询不出来。"
        return False
    all_length = count[0].get('count')
    end1 = datetime.datetime.now()
    print "查询时间结束",end1.strftime('%Y-%m-%D %H:%M:%S')
    print "查询耗时间",end1-start1
    end = r.get("lcc_init" + root_category)
    end = int(end) if end else 0
    while True:
        if end < all_length:
            select_from_source_db(root_category,end)
            end += config.LENGTH
            r.set("lcc_init" + root_category,end)
        else:
            break


if __name__ == "__main__":
    start = datetime.datetime.now()
    print "start",start.strftime('%Y-%m-%D %H:%M:%S')
    for root_cate in config.ROOT_CATEGORY:
        print '==========source/desc/child表 品类ID：', root_cate, '数据插入操作start=========='
        main_threads(root_cate)
        print '==========source/desc/child表 品类ID：', root_cate, '数据插入操作end=========='
    end = datetime.datetime.now()
    print "end", end.strftime('%Y-%m-%D %H:%M:%S')
    print "终于u结束了呀", end-start

