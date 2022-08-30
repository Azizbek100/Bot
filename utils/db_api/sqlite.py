import sqlite3
# from loader import db

class Database:

    def __init__(self, path_to_db='data/customer.db'):
    
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
        CREATE TABLE Verified (
            id integer primary key,
            telegram_id int,
            name varchar(20),
            zakaz text,
            price real
        );"""
        self.execute(sql, commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())


    def add_user(self, fullname: str, telegram_id: int, language: str):
        # SQL_EXAMPLE = "INSERT INTO BotUsers(fullname, telegram_id, language) VALUES(1, 'John', 'John@gmail.com')"

        sql = """
        insert into BotUsers(fullname, telegram_id, language) VALUES(?, ?, ?)
        """
        self.execute(sql, parameters=(fullname, telegram_id, language), commit=True)

    def select_all_users(self):
        sql = """
        SELECT * FROM BotUsers;
        """
        return self.execute(sql=sql, fetchall=True)

    def add_user(self, fullname, tel_id, language):
        # SQL_EXAMPLE = "INSERT INTO Users(id, Name, email) VALUES(1, 'John', 'John@gmail.com')"
        
        sql = """
        INSERT INTO BotUsers(fullname, telegram_id, language) VALUES(?, ?, ?)
        """
        self.execute(sql, parameters=(fullname, tel_id, language), commit=True)

    def select_all_users(self):
        sql = """
        SELECT * FROM BotUsers;
        """
        return self.execute(sql, fetchall=True)

    def select_user(self, **kwargs):
        # SQL_EXAMPLE = "SELECT * FROM Users where id=1 AND Name='John'"
        sql = "SELECT * FROM BotUsers WHERE True;"
        sql, parameters = self.format_args(sql, kwargs)

        return self.execute(sql, parameters=parameters, fetchone=True)


    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM BotUsers;", fetchone=True)


    def delete_users(self):
        self.execute("DELETE FROM BotUsers WHERE TRUE", commit=True)

    def add_product(self, pro_name, price, image):
        sql = """insert into Products (product, price, image)
        values (?, ?, ?);
        """
        self.execute(sql=sql, parameters=(pro_name, price, image), commit=True)


    def add_zakaz(self, tel_id, fullname, product, amount, price):
        sql = """insert into Delivered (telegram_id, name, product, amount, price)
        values (?, ?, ?, ?, ?)
        """
        self.execute(sql=sql, parameters=(tel_id, fullname, product, amount, price), commit=True)
        
    def check_zakaz(self, tel_id, pro_name):
        sql = """select product, amount
        from Delivered
        where telegram_id = ? and product = ?;
        """
        return self.execute(sql=sql, parameters=(tel_id, pro_name), fetchall=True)

    def update_checked_zakaz(self, teleg_id, prod_name, current_amount):
        sql = """update Delivered
        set amount = ?
        where telegram_id = ?
        and product = ?;
        """
        self.execute(sql=sql, parameters=(current_amount, teleg_id, prod_name), commit=True)

    def get_product(self, name):
        sql = """select product, price, image
        from Products
        where product = ?;
        """
        return self.execute(sql=sql, parameters=(name, ), fetchone=True)

    def get_korzinka(self, teleg_id):
        sql = """select product, amount, price
        from Delivered
        where telegram_id = ?;
        """
        return self.execute(sql=sql, parameters=(teleg_id, ), fetchall=True)

    def clear_del(self, tel_id):
        sql = """delete from Delivered
        where telegram_id = ?
        """
        self.execute(sql=sql, parameters=(tel_id, ), commit=True)

    def clear_current(self, calldata, tel_id):
        sql = """delete from Delivered
        where callback = ?
        and telegram_id = ?;
        """
        self.execute(sql=sql, parameters=(calldata, tel_id), commit=True)

    def set_call(self, calldata, tel_id, product):
        sql = """update Delivered
        set callback = ?
        where telegram_id = ?
        and product = ?;
        """
        self.execute(sql=sql, parameters=(calldata, tel_id, product), commit=True)

    def alter_table(self):
        sql = """alter table Delivered
        add callback varchar(100) null;
        """
        self.execute(sql=sql, commit=True)
    
    def inserttable(self, tel_id, name, zakaz, total):
        sql = """insert into Verified (telegram_id, name, zakaz, price)
        values (?, ?, ?, ?);
        """
        self.execute(sql=sql, parameters=(tel_id, name, zakaz, total), commit=True)

    def get_zakaz(self, tel_id):
        sql = """select * from Verified
        where telegram_id = ?;
        """
        return self.execute(sql=sql, parameters=(tel_id, ), fetchone=True)

    def get_next(self, user, tel_id):
        sql = """select * from Verified
        where telegram_id = ?
        and id > ?;
        """
        return self.execute(sql=sql, parameters=(tel_id, user), fetchone=True)

    def get_prev(self, user, tel_id):
        sql = """select * from Verified
        where telegram_id = ?
        and id < ?;
        """
        return self.execute(sql=sql, parameters=(tel_id, user), fetchall=True)

    def get_pay_order(self, tel_id, pay_id):
        sql = """select * from Verified
        where telegram_id = ?
        and id = ?;
        """
        return self.execute(sql=sql, parameters=(tel_id, pay_id), fetchone=True)

def logger(statement):
    print(f"""
_____________________________________________________
Executing:
{statement}
_____________________________________________________
""")