# encoding:utf-8

import MySQLdb
from DBUtils.PooledDB import PooledDB

class UtilsMySQL(object):

    def __init__(self,db):
        self.__pool = PooledDB(creator=MySQLdb, mincached=1, maxcached=20,host=db['host'], user=db['user'],passwd=db['password'], db=db['db'],port=db['port'],charset="utf8")

    def __get_connection(self):
        """
        @summary: 静态方法，从连接池中取出连接
        @return MySQLdb.connection
        """
        return self.__pool.connection()

    def create_table_or_not(self, table_name, create_sql):
        """
        判断创建或者不创建表，并执行操作
        :return:
        """
        _sql = 'show tables like "%s";' % table_name
        conn = self.__get_connection()
        cur = conn.cursor()
        res = cur.execute(_sql)
        if not res:
            try:
                cur.execute(create_sql)
                conn.commit()
            except Exception as e:
                print str(e), '表', table_name, '没有创建成功'
                return None
        return table_name

    def execute_sql_query(self, sql):
        """
        执行sql，返回结果
        :param sql:
        :return:
        """
        res = []
        conn = self.__get_connection()
        cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        count = cur.execute(sql)
        if count>0:
            res = cur.fetchall()
        return res

    def execute_sql_cud(self,sql):
        """
        执行sql
        :param sql:
        :return:
        """
        conn = self.__get_connection()
        cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cur.execute(sql)
        conn.commit()


