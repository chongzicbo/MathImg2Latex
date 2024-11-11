from loguru import logger
import pymysql
from pymysql.err import OperationalError
import os
from time import time

logger.add("./logs/server.log", rotation="10 MB")


class MysqlConfig:
    MYSQL_HOST = "127.0.0.1"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "root"
    MYSQL_DB = "nlp_test"
    MYSQL_CHARSET = "utf8mb4"
    MYSQL_PORT = 3306


# 配置MySQL数据库连接
class Database:
    def __init__(self):
        try:
            self.connection = pymysql.connect(
                host=MysqlConfig.MYSQL_HOST,
                user=MysqlConfig.MYSQL_USER,
                password=MysqlConfig.MYSQL_PASSWORD,
                db=MysqlConfig.MYSQL_DB,
                charset=MysqlConfig.MYSQL_CHARSET,
                port=MysqlConfig.MYSQL_PORT,
                cursorclass=pymysql.cursors.DictCursor,
            )
        except OperationalError as e:
            if e.args[0] in (2003, 2006, 2013, 2014):
                # 这些错误码通常表示连接问题
                self.reconnect()
            else:
                raise

    def reconnect(self):
        for _ in range(3):  # 尝试重新连接3次
            try:
                self.connection.ping(reconnect=True)
                return
            except OperationalError as e:
                if _ < 2:  # 如果还没有尝试3次，等待1秒后重试
                    time.sleep(1)
                else:
                    raise

    def execute(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                self.connection.commit()
        except OperationalError as e:
            if e.args[0] in (2003, 2006, 2013, 2014):
                self.reconnect()
                self.execute(query, params)  # 重新执行查询
            else:
                raise

    def fetchone(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()
        except OperationalError as e:
            if e.args[0] in (2003, 2006, 2013, 2014):
                self.reconnect()
                return self.fetchone(query, params)  # 重新执行查询
            else:
                raise


images_formulas_saved_dir = "/data/bocheng/data/test/images_formulas"
os.makedirs(images_formulas_saved_dir, exist_ok=True)
