from loguru import logger

logger.add("./logs/server.log", rotation="10 MB")


class MysqlConfig:
    MYSQL_HOST = "127.0.0.1"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "123456"
    MYSQL_DB = "test"
    MYSQL_CHARSET = "utf8mb4"
