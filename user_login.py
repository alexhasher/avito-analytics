import FDataBase
from config import user, password, host, db_name

class UserLogin:
    def fromDB(self, user_id):
        fdb = FDataBase.FDataBase(host, user, password, db_name)
        self.__user = fdb.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user['id'])