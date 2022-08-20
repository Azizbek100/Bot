import sqlite3
from loader import db

class Database:
    def __init__(self, path_to_db=db.path_to_db):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data

    def create_table_users(self):
        sql = """
        CREATE TABLE BotUsers (
            id integer primary key,
            fullname varchar(255) NOT NULL,
            telegram_id int unique,
            language varchar(3)
            );
"""
        self.execute(sql, commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(self, fullname, tel_id, language):
        # SQL_EXAMPLE = "INSERT INTO Users(id, Name, email) VALUES(1, 'John', 'John@gmail.com')"

        sql = """
        INSERT INTO BotUsers(fullname, telegram_id, language) VALUES(?, ?, ?)
        """
        self.execute(sql, parameters=(fullname, tel_id, language), commit=True)

    def select_all_users(self):
        sql = """
        SELECT * FROM BotUsers
        """
        return self.execute(sql, fetchall=True)

    def select_user(self, **kwargs):
        # SQL_EXAMPLE = "SELECT * FROM Users where id=1 AND Name='John'"
        sql = "SELECT * FROM BotUsers WHERE "
        sql, parameters = self.format_args(sql, kwargs)

        return self.execute(sql, parameters=parameters, fetchone=True)

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM BotUsers;", fetchone=True)

    # def update_user_email(self, email, id):
    #     # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

    #     sql = f"""
    #     UPDATE Users SET email=? WHERE id=?
    #     """
    #     return self.execute(sql, parameters=(email, id), commit=True)

    def delete_users(self):
        self.execute("DELETE FROM BotUsers WHERE TRUE", commit=True)


def logger(statement):
    print(f"""
_____________________________________________________
Executing:
{statement}
_____________________________________________________
""")

a = Database()    
a.create_table_users()
