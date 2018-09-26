import sys
import psycopg2
from .dbcfg import HOST, PORT, DB_NAME, USER, PASSWORD, ADMIN, ADM_PASS, ENCODING, TABLESPACE, CONNECTION_LIMIT, connect_string
from . import dblog

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
            dblog.dbtools_logger.error(f'DB creation error: {sys.exc_info()[0:2]}')

    def create_brands(self):
        try:
           self.cursor.execute(f'CREATE TABLE {DB_NAME}.public."BRANDS" ('
                                   f'ID serial NOT NULL,'
                                   f'BRAND varchar(20) NOT NULL,'
                                   f'CONSTRAINT BRANDS_pkey PRIMARY KEY (ID))')
        except:
            dblog.dbtools_logger.error(f'Brands table creation error: {sys.exc_info()[0:2]}')

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
            dblog.dbtools_logger.error(f'Models table creation error: {sys.exc_info()[0:2]}')

    def create_sort_proc(self):
        try:
            with open('dbapi/sort_cars.txt') as file:
                script = file.read()
            self.cursor.execute(script)
        except:
            dblog.dbtools_logger.error(f'Sorting procedure creation error: {sys.exc_info()[0:2]}')

    def create_all(self):
        self.create_brands()
        self.create_models()
        self.create_sort_proc()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()


class Base_Updater():

    __slots__ = ['connection', 'cursor']

    def __init__(self):
        pass

    def start_updating(self):
        try:
            connection = psycopg2.connect(connect_string)
            connection.autocommit = True
            cursor = connection.cursor()
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
            dblog.dbtools_logger.error(f'Preparing updating error: {sys.exc_info()[0:2]}')

    def round5_mileage(self, item):
        try:
            mileage = int(item['kmage'])
            result = round(mileage/5000)*5000
            item['kmage'] = str(result)
        except KeyError:
            dblog.dbtools_logger.error(f'No such key in items.keys(): {sys.exc_info()[1]}')
        except:
            dblog.dbtools_logger.error(f'DB Updater internal error: {sys.exc_info()[0:2]}')

    def update(self, item):
        try:
            self.round5_mileage(item)
            columns = ', '.join(tuple(item.keys()))
            values = '\', \''.join(tuple(item.values()))
            self.cursor.execute(f'INSERT INTO "CARS_DUMP" ({columns.lower()}) VALUES (\'{values}\')')
        except:
            dblog.dbtools_logger.error(f'Updating error: {sys.exc_info()[0:2]}')

    def end_updating(self):
        try:
            self.cursor.execute('SELECT sort_cars()')
            self.connection.close()
        except:
            dblog.dbtools_logger.error(f'Finishing updating error: {sys.exc_info()[0:2]}')


class Data_Getter():
    __slots__ = ['connection', 'cursor']

    def __init__(self):
        pass

    def connect(self):
        try:
            self.connection = psycopg2.connect(connect_string)
            self.cursor = self.connection.cursor()
        except:
            dblog.dbtools_logger.error(f'DB connection error: {sys.exc_info()[0:2]}')

    def disconnect(self):
        try:
            self.connection.close()
        except:
            dblog.dbtools_logger.error(f'DB connection error: {sys.exc_info()[0:2]}')

    def _round5_mileage(self, item):
        try:
            mileage = int(item['kmage'])
            result = round(mileage/5000)*5000
            item['kmage'] = str(result)
        except KeyError:
            dblog.dbtools_logger.error(f'No such key in items.keys(): {sys.exc_info()[1]}')
        except:
            dblog.dbtools_logger.error(f'DB Getter internal error: {sys.exc_info()[0:2]}')

    def _get_tabname(self, item):
        try:
            tabname = '_'.join((item['brand'], item['model']))
            return tabname
        except KeyError:
            dblog.dbtools_logger.error(f'No such keys in items.keys(): {sys.exc_info()[1]}')
        except:
            dblog.dbtools_logger.error(f'DB Getter internal error: {sys.exc_info()[0:2]}')

    def _get_result_from_cursor(self):
        try:
            result = []
            for item in self.cursor.fetchall():
                result.append(*item)
            return result
        except:
            dblog.dbtools_logger.error(f'DB Getter internal error: {sys.exc_info()[0:2]}')

    def get_brands(self):
        try:
            self.connect()
            self.cursor.execute('SELECT brand FROM "BRANDS"')
            result = self._get_result_from_cursor()
            self.disconnect()
            return result
        except:
            dblog.dbtools_logger.error(f'Brands list getting filed: {sys.exc_info()[0:2]}')

    def get_models(self, brandname):
        try:
            self.connect()
            self.cursor.execute(f'SELECT model FROM "MODELS" WHERE '
                                    f'brand_id = (SELECT id FROM "BRANDS" WHERE brand = \'{brandname}\')')
            result = self._get_result_from_cursor()
            self.disconnect()
            return result
        except:
            dblog.dbtools_logger.error(f'Models list getting filed: {sys.exc_info()[0:2]}')

    def get_price(self, item, count = 7):
        try:
            self._round5_mileage(item)
            self.connect()
            tabname = self._get_tabname(item)

            self.cursor.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\'')

            for name in self.cursor.fetchall():
                if tabname == name[0]:
                    break
            else:
                self.disconnect()
                dblog.dbtools_logger.error(f'No such table in DB: {tabname}')
                return False

            self.cursor.execute(f'SELECT avg_price FROM "{tabname}" '
                                    f'WHERE kmage = \'{item["kmage"]}\' '
                                    f'AND year = \'{item["year"]}\' '
                                    f'ORDER BY id DESC '
                                    f'LIMIT {count} ')
            result = self._get_result_from_cursor()
            self.disconnect()
            return result
        except:
            dblog.dbtools_logger.error(f'Price getting filed: {sys.exc_info()[0:2]}')
