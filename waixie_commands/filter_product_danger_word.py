# -*- coding: utf-8 -*-

import datetime
import sys
sys.path.append('..')
from util.util import *

reload(sys)
sys.setdefaultencoding('utf8')


def daily_filter_product_danger_word():
    reg = 'waixie_product_source_[0-9]+'
    results = select_waixie_tables(reg)

    danger_words = get_danger_word(1)

    danger_word_list = []
    for word in danger_words:
        danger_word = word.get('danger_word')
        if danger_word:
            danger_word_list.append(danger_word)

    danger_word_reg = '|'.join(danger_word_list)

    if danger_word_reg:
        for table in results:
            sql = """update {table_name} set status=2,sign_type=2,update_date='{source_update_date}',update_user=0 
                      WHERE title REGEXP '{danger_word_reg}'
                  """.format(table_name=table,
                             source_update_date=datetime.datetime.now(tz=utc_tz).strftime('%Y-%m-%d %H:%M:%S'),
                             danger_word_reg=danger_word_reg)
            waixie_db_manger.execute_sql_cud(sql)

    danger_word_sql = """
        update waixie_sensitive_word set filter_mark = 0,update_date='{danger_update_date}',update_user=0 
        WHERE danger_word in ('{danger_word_list}')
    """.format(danger_update_date=datetime.datetime.now(tz=utc_tz).strftime('%Y-%m-%d %H:%M:%S'),
               danger_word_list="','".join(danger_word_list))

    waixie_db_manger.execute_sql_cud(danger_word_sql)


if __name__ == "__main__":
    start = datetime.datetime.now()
    print "start",start.strftime('%Y-%m-%d %H:%M:%S')

    daily_filter_product_danger_word()

    end = datetime.datetime.now()
    print "end", end.strftime('%Y-%m-%d %H:%M:%S')
    print "终于u结束了呀", end-start

