import pymysql


class FDataBase:
    def __init__(self, host, user, password, db_name):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name

    def getUser(self, user_id):
        try:
            connection = pymysql.connect(
                host=self.host,
                port=3306,
                user=self.user,
                password=self.password,
                database=self.db_name,
                cursorclass=pymysql.cursors.DictCursor
            )
            print("Успешное соединение с", db_name)
            try:
                with connection.cursor() as cursor:
                    insert_query = f"SELECT * FROM users WHERE id = {user_id} LIMIT 1"
                    cursor.execute(insert_query)
                    res = cursor.fetchone()
                    if not res:
                        print("Пользователь не найден")
                        return False
                    return res
            except Exception as ex:
                print(ex)
                print("Ошибка получения данных из", self.db_name)
            finally:
                connection.close()
        except Exception as ex:
            print(ex)
            print("Не удалось установить соединение с", self.db_name)


    def getUserByEmail(self, email):
        try:
            connection = pymysql.connect(
                host=self.host,
                port=3306,
                user=self.user,
                password=self.password,
                database=self.db_name,
                cursorclass=pymysql.cursors.DictCursor
            )
            print("Успешное соединение с", self.db_name)
            try:
                with connection.cursor() as cursor:
                    insert_query = f"SELECT * FROM users WHERE email = '{email}' LIMIT 1"
                    cursor.execute(insert_query)
                    res = cursor.fetchone()
                    if not res:
                        print("Пользователь не найден")
                        return False
                    print(res)
                    return res
            except Exception as ex:
                print(ex)
                print("Ошибка получения данных из", self.db_name)
            finally:
                connection.close()
        except Exception as ex:
            print(ex)
            print("Не удалось установить соединение с", self.db_name)
        return False