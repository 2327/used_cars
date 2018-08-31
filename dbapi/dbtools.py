import psycopg2
from dbcfg import HOST, PORT, DB_NAME, USER, PASSWORD, ADMIN, ADM_PASS, ENCODING, TABLESPACE, CONNECTION_LIMIT
import dblog

class Base_Creator():

    __slots__ = ['connection', 'cursor']

    def __init__(self):
        self.connection = ''

    def __enter__(self):
        self.get_psyco('postgres')
        self.create_base()
        self.get_psyco(DB_NAME)
        return self

    def get_psyco(self, database):
        if self.connection:
            self.connection.close()
        self.connection = psycopg2.connect(host=HOST, port=PORT, user=ADMIN, password=ADM_PASS, dbname = database)
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()

    def create_base(self):
        try:
            self.cursor.execute(f'CREATE DATABASE {DB_NAME} WITH '
                                    f'OWNER = {ADMIN} '
                                    f'ENCODING = {ENCODING} '
                                    f'TABLESPACE = {TABLESPACE} '
                                    f'CONNECTION LIMIT = {CONNECTION_LIMIT}')
            self.cursor.execute(f'GRANT ALL ON DATABASE {DB_NAME} TO {ADMIN}')
        except:
            dblog.log('DB_ERROR')

    def create_brands(self):
        try:
           self.cursor.execute(f'CREATE TABLE {DB_NAME}.public."BRANDS" ('
                               f'ID serial NOT NULL,'
                               f'BRAND varchar(20) NOT NULL,'
                               f'CONSTRAINT BRANDS_pkey PRIMARY KEY (ID))')
        except:
            dblog.log('DB_ERROR')

    def create_models(self):
        try:
            self.cursor.execute(f'CREATE TABLE {DB_NAME}.public."MODELS" ('
                               f'ID serial NOT NULL,'
                               f'BRAND_ID integer NOT NULL,'
                               f'MODEL varchar(20) NOT NULL,'
                               f'CONSTRAINT MODELS_pkey PRIMARY KEY (ID),'
                               f'CONSTRAINT BRAND_MODEL_link FOREIGN KEY (BRAND_ID) '
                               f'REFERENCES {DB_NAME}.public."BRANDS"(ID) '
                               f'ON DELETE CASCADE)')
        except:
            dblog.log('DB_ERROR')

    def create_all(self):
        self.create_brands()
        self.create_models()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()


class Base_Updater():

    __slots__ = ['connection', 'cursor']

    def __init__(self):
        pass

    def start_updating(self):
        try:
            connection = psycopg2.connect(host=HOST, port=PORT, dbname=DB_NAME, user=USER, password=PASSWORD)
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\'')

            for table_name in cursor.fetchall():       #Этот цикл - заглушка. В будущем сортировщик будет дропать таблицу
                if 'CARS_DUMP' in table_name[0]:
                    cursor.execute('DROP TABLE public."CARS_DUMP"')

            cursor.execute('CREATE TABLE public."CARS_DUMP" ('
                               'ID serial NOT NULL,'
                               'BRAND varchar(20) NOT NULL,'
                               'MODEL  varchar(20) NOT NULL,'
                               'YEAR  smallint NOT NULL,'
                               'KMAGE  integer NOT NULL,'
                               'PRICE integer NOT NULL,'
                               'CONSTRAINT CARS_DUMP_pkey PRIMARY KEY (ID));')
            self.connection = connection
            self.cursor = cursor
            return self.cursor
        except:
            dblog.log('DB_ERROR')

    def round5_mileage(self, item):
        mileage = int(item['kmage'])
        result = round(mileage/5000)*5000
        item['kmage'] = str(result)

    def update(self, item):
        try:
            self.round5_mileage(item)
            columns = ', '.join(tuple(item.keys()))
            values = '\', \''.join(tuple(item.values()))
            self.cursor.execute(f'INSERT INTO public."CARS_DUMP" ({columns.lower()}) VALUES (\'{values}\')')
        except:
            dblog.log('DB_ERROR')

    def end_updating(self):
        try:
            #self.cursor.execute('SORT_ITEMS')
            self.connection.close()
        except:
            dblog.log('DB_ERROR')


class Data_Getter():
    __slots__ = ['connection', 'cursor']

    def __init__(self):
        pass

    def connect(self):
        self.connection = psycopg2.connect(host=HOST, port=PORT, user=ADMIN, password=ADM_PASS, dbname=DB_NAME)
        self.cursor = self.connection.cursor()

    def disconnect(self):
        self.connection.close()

    def round5_mileage(self, item):
        mileage = int(item['kmage'])
        result = round(mileage/5000)*5000
        item['kmage'] = str(result)

    def get_brands(self): #Заглушка. После написания обработчика код будет изменен
        self.connect()
        self.cursor.execute('SELECT DISTINCT brand FROM public."CARS_DUMP"')
        result = []
        for brand in self.cursor.fetchall():
            result.append(*brand)
        self.disconnect()
        return result

    def get_models(self): #Заглушка. После написания обработчика код будет изменен
        self.connect()
        self.cursor.execute('SELECT DISTINCT model FROM public."CARS_DUMP"')
        result = []
        for model in self.cursor.fetchall():
            result.append(*model)
        self.disconnect()
        return result

    def get_price(self, item):
        self.round5_mileage(item)
        self.connect()
        self.cursor.execute(f'SELECT AVG(price) FROM public."CARS_DUMP" WHERE '
                            f'brand = \'{item["brand"]}\' AND '
                            f'model = \'{item["model"]}\' AND '
                            f'year = \'{item["year"]}\' AND '
                            f'kmage = \'{item["kmage"]}\'')
        result = self.cursor.fetchone()[0]
        return result
