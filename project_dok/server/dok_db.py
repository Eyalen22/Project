import sqlite3

class MyDB:

    def __init__(self):
        self.db_Name = "DOK_DB.sql"
        self.conn = None
        self.cursor = None
        self._create()


    def _create(self):
        '''
        create DB
        :return: None
        '''
        self.conn = sqlite3.connect(self.db_Name)
        self.cursor = self.conn.cursor()

        sql_users = "CREATE TABLE IF NOT EXISTS users (username VARCHAR(10) PRIMARY KEY,password_hash VARCHAR(64), mail VARCHAR(50));"
        sql_dok = "CREATE TABLE IF NOT EXISTS doks (username VARCHAR(10) PRIMARY KEY, dok VARCHAR(20));"
        self.create(sql_users)
        self.create(sql_dok)


    def create(self, sql):
        """create a list if needed"""
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            pass

    def _user_exist(self, username):
        '''
        checks if user exist - return username, else return None
        :param username: str
        :return: return the username if student exist else none
        '''
        sql = f"SELECT * FROM users WHERE username = ?"
        self.cursor.execute(sql, (username,))
        return not self.cursor.fetchone() is None

    def _dok_exist(self, dok_name):
        '''
        checks if dok exist - return dok_name, else return None
        :param dok_name: str
        :return: return the dok_name if student exist else none
        '''
        sql = f"SELECT * FROM doks WHERE dok = ?"
        self.cursor.execute(sql, (dok_name,))
        return not self.cursor.fetchone() is None


    def user_dok_match(self, user_name, dok_name):
        '''
        Checks if a specific user owns a specific DOK.
        :param user_name: str
        :param dok_name: str
        :return: True if the match exists, False otherwise
        '''
        sql = "SELECT * FROM doks WHERE username = ? AND dok = ?"
        self.cursor.execute(sql, (user_name, dok_name))
        return not self.cursor.fetchone() is None


    def add_user(self, username, password, mail):
        '''
        add user data
        :param username: str
        :param password: str
        :param mail: str
        :return: true if seccses else false
        '''
        status = False
        if not self._user_exist(username):
            sql = f"INSERT INTO users VALUES (?,?,?)"
            self.cursor.execute(sql, (username,password,mail))
            self.conn.commit()
            status = True

        return status

    def add_dok(self, username, dok_name):
        """
        add dok data
        :param username:str
        :param dok_name: str
        :return: true if seccses else false
        """
        status = False
        if not self._dok_exist(dok_name):
            sql = f"INSERT INTO doks VALUES (?,?)"
            self.cursor.execute(sql, (username,dok_name))
            self.conn.commit()
            status = True

        return status


    def update_mail(self, username, mail):
        '''
        update new mail
        :param username: str
        :param mail: str
        :return: true if seccses else false
        '''
        status = False
        if self._user_exist(username):
            sql = f"UPDATE users SET mail = ? WHERE username = ?"
            self.cursor.execute(sql, (mail, username))
            self.conn.commit()
            status = True
        return status

    def get_mail(self, user_name):
        """"""
        try:
            sql = "SELECT mail FROM users WHERE username = ?"
            self.cursor.execute(sql, (user_name,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            print(f"Error retrieving email: {e}")
            return None


if __name__ == '__main__':
    myDB = MyDB()
    myDB.add_user("noam", "12345", "eyal@gmail.com")
    myDB.add_dok("noam", "dok1")
    print(myDB.user_dok_match("noam", "dok2"))
    print(myDB.user_dok_match("noam", "dok1"))
    print(myDB.get_mail("noam"))
    myDB.update_mail("noam", "raniSomb@gmail.com")
    print(myDB.get_mail("noam"))


