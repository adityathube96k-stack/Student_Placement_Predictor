import pymysql
from config import Config


def get_connection():
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )


def test_connection():

    connection = None

    try:

        connection = get_connection()

        with connection.cursor() as cursor:

            cursor.execute("SELECT 1 AS test")

            result = cursor.fetchone()

        return True, "MySQL connection successful."

    except Exception as error:

        return False, str(error)

    finally:

        if connection:
            connection.close()