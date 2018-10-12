"""This module contains the tools to create and update used cars database and to get data.
For using this module you have to install psycopg2 db driver.
You can change DB settings in dbcfg.py

    To create used cars database you should open terminal in used_cars directory and enter "python -m dbapi.create_db"
command.

    Base_Updater class provide DB update mechanism. DB updating performed in several steps:
    1. You should to create Base_Updater instance (for example "updater").
    2. Then execute updater.start_updating() command that prepare environment for DB update:
        - create connection to DB and cursor to queries execution;
        - create table "CARS_DUMP" - buffer for new data about cars.
    3. Now you can put your data into DB. Prepare the items - dicts contains such keys: brand, model, year, kmage,
    price, engine, gearbox.
    Remember that values can't be empty! Then use updater.update(item) method for all your items.
    4. Finally use updater.end_update() method. This method performs sort function that sorting all new data in DB then
    closing connection to DB.

    To get data from DB you can use Data_Getter class. You should create the instance for use it! Data_Getter provides
several methods to get data about used cars from DB (for example DG instance called "getter"):
    1. getter.get_brands() return list contains all used cars brands from DB;
    2. getter.get_models(brandname) return list of all used cars models for brand "brandname" from DB;
    3. getter.get_years(brandname, modelname) return list of all used cars years of manufacture for brand "brandname"
    and model "modelname" from DB;
    4. getter.get_engines(brandname, modelname, year) return list of all engines for described brand, model
    and year of manufacture from DB;
    5. getter.get_gearbox(brandname, modelname, year, engine) return list of all gearboxes for described brand, model,
    engine and year of manufacture from DB;
    6. getter.get_avg_price(item) return the average price for car was described in "item" dict. Dict have to contain
    such keys: brand, model, year, kmage, engine, gearbox.
    7. getter.get_prices(item) return list of all prices was got from last update for car was described in "item" dict.
    8. getter.get_points(item) return list with 5 numbers. Each number is count of prices was got from last update which
    value is in certain range relative to average car price:
        0) the zero element: count of prices that less than 0.8*avg_price
        1) the first element: greater or equal to 0.8 but less than 0.95*avg_price
        2) the second element: greater or equal to 0.95 but less or equal t0 1.05*avg_price
        3) the third element: greater than 1.05 but less or equal to 1.2*avg_price
        4) the fourth element: greater than 1.2*avg_price"""


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
            dblog.dbtools_logger.debug(f'Base_Creator.create_base() was executed with internal args: \n'
                                       f'DATABASE {DB_NAME}\n'
                                       f'OWNER = {ADMIN}\n'
                                       f'ENCODING = {ENCODING}\n'
                                       f'TABLESPACE = {TABLESPACE}\n'
                                       f'CONNECTION LIMIT = {CONNECTION_LIMIT}\n')

    def create_dict_tab(self):
        try:
           self.cursor.execute(f'CREATE TABLE {DB_NAME}.public."CARS" ('
                                   f'ID serial NOT NULL,'
                                   f'BRAND varchar(20) NOT NULL,'
                                   f'MODEL varchar(20) NOT NULL,'
                                   f'CONSTRAINT BRANDS_pkey PRIMARY KEY (ID))')
        except:
            dblog.dbtools_logger.error(f'Dict table creation error: {sys.exc_info()[0:2]}')
            dblog.dbtools_logger.debug(f'Base_Creator.create_dict_tab() was executed with internal args: \n'
                                       f'TABLE {DB_NAME}')

    def create_sort_proc(self):
        try:
            with open('dbapi/sort_cars.txt') as file:
                script = file.read()
            self.cursor.execute(script)
        except:
            dblog.dbtools_logger.error(f'Sorting procedure creation error: {sys.exc_info()[0:2]}')

    def create_all(self):
        self.create_dict_tab()
        # self.create_models()
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
                               'ENGINE varchar(20) NOT NULL,'
                               'GEARBOX varchar(20) NOT NULL,'
                               'CONSTRAINT CARS_DUMP_pkey PRIMARY KEY (ID));')
            self.connection = connection
            self.cursor = cursor
            return self.cursor
        except:
            dblog.dbtools_logger.error(f'Preparing updating error: {sys.exc_info()[0:2]}')
            dblog.dbtools_logger.debug(f'Base_Updater.start_updating() was executed with internal args: \n'
                                       f'connect string = {connect_string}')

    def round5_mileage(self, item):
        try:
            mileage = int(item['kmage'])
            result = round(mileage/5000)*5000
            item['kmage'] = str(result)
        except KeyError:
            dblog.dbtools_logger.error(f'No such key in items.keys(): {sys.exc_info()[1]}')
            dblog.dbtools_logger.debug(f'Base_Updater.round5_mileage() was executed with args: \n'
                                       f'item = {item}')
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
            dblog.dbtools_logger.debug(f'Base_Updater.update() was executed with args: \n'
                                       f'item = {item}')

    def end_updating(self):
        try:
            self.cursor.execute('SELECT sort_cars()')
            self.connection.close()
        except:
            dblog.dbtools_logger.error(f'Finishing updating error: {sys.exc_info()[0:2]}')


class Data_Getter():
    __slots__ = ['connection', 'cursor', 'current_id']

    def __init__(self):
        pass

    def connect(self):
        try:
            self.connection = psycopg2.connect(connect_string)
            self.cursor = self.connection.cursor()
        except:
            dblog.dbtools_logger.error(f'DB connection error: {sys.exc_info()[0:2]}')
            dblog.dbtools_logger.debug(f'Data_Getter.connect() was executed with internal args: \n'
                                       f'connect_string = {connect_string}')

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
            dblog.dbtools_logger.debug(f'Data_Getter._round5_mileage() was executed with args: \n'
                                       f'item = {item}')
        except:
            dblog.dbtools_logger.error(f'DB Getter internal error: {sys.exc_info()[0:2]}')

    def _get_tabname(self, item):
        try:
            tabname = '_'.join((item['brand'], item['model']))
            self.cursor.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\'')
            for name in self.cursor.fetchall():
                if tabname == name[0]:
                    break
            else:
                self.disconnect()
                dblog.dbtools_logger.error(f'No such table in DB: {tabname}')
                return False
            return tabname
        except KeyError:
            dblog.dbtools_logger.error(f'No such keys in items.keys(): {sys.exc_info()[1]}')
            dblog.dbtools_logger.debug(f'Data_Getter._get_tabname() was executed with args: \n'
                                       f'item = {item}')
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
            self.cursor.execute('SELECT DISTINCT brand FROM "CARS"')
            result = self._get_result_from_cursor()
            self.disconnect()
            return result
        except:
            dblog.dbtools_logger.error(f'Brands list getting failed: {sys.exc_info()[0:2]}')

    def get_models(self, brandname):
        try:
            self.connect()
            self.cursor.execute(f'SELECT model FROM "CARS" WHERE '
                                    f'brand = \'{brandname}\'')
            result = self._get_result_from_cursor()
            self.disconnect()
            return result
        except:
            dblog.dbtools_logger.error(f'Models list getting failed: {sys.exc_info()[0:2]}')
            dblog.dbtools_logger.debug(f'Data_Getter.get_models() was executed with args: \n'
                                       f'brandname = {brandname}')

    def get_years_for_model(self, brandname, modelname):
        try:
            self.connect()
            tabname = self._get_tabname({'brand': brandname, 'model': modelname})
            if tabname:
                self.cursor.execute(f'SELECT DISTINCT year FROM "{tabname}"')
                result = self._get_result_from_cursor()
                self.disconnect()
                return result
            else:
                return False
        except:
            dblog.dbtools_logger.error(f'Years getting failed: {sys.exc_info()[0:2]}')
            dblog.dbtools_logger.debug(f'Data_Getter.get_years_for_model() was executed with args: \n'
                                       f'brandname = {brandname}\n'
                                       f'modelname = {modelname}')

    def get_engines(self, brandname, modelname, year):
        try:
            self.connect()
            tabname = self._get_tabname({'brand': brandname, 'model': modelname})
            if tabname:
                self.cursor.execute(f'SELECT DISTINCT engine FROM "{tabname}" '
                                        f'WHERE year = \'{year}\'')
                result = self._get_result_from_cursor()
                self.disconnect()
                return result
            else:
                return False
        except:
            dblog.dbtools_logger.error(f'Engines getting failed: {sys.exc_info()[0:2]}')
            dblog.dbtools_logger.debug(f'Data_Getter.get_engines() was executed with args: \n'
                                       f'brandname = {brandname}\n'
                                       f'modelname = {modelname}\n'
                                       f'year = {year}')

    def get_gearboxes(self, brandname, modelname, year, engine):
        try:
            self.connect()
            tabname = self._get_tabname({'brand': brandname, 'model': modelname})
            if tabname:
                self.cursor.execute(f'SELECT DISTINCT gearbox FROM "{tabname}" '
                                        f'WHERE year = \'{year}\' '
                                        f'AND engine = \'{engine}\'')
                result = self._get_result_from_cursor()
                self.disconnect()
                return result
            else:
                return False
        except:
            dblog.dbtools_logger.error(f'Gearboxes getting failed: {sys.exc_info()[0:2]}')
            dblog.dbtools_logger.debug(f'Data_Getter.get_gearboxes() was executed with args: \n'
                                       f'brandname = {brandname}\n'
                                       f'modelname = {modelname}\n'
                                       f'year = {year}\n'
                                       f'engine = {engine}')

    def get_avg_price(self, item, count = 7):
        try:
            self._round5_mileage(item)
            self.connect()
            tabname = self._get_tabname(item)
            if tabname:
                self.cursor.execute(f'SELECT avg_price FROM "{tabname}" '
                                        f'WHERE kmage = \'{item["kmage"]}\' '
                                        f'AND year = \'{item["year"]}\' '
                                        f'ORDER BY id DESC '
                                        f'LIMIT {count} ')
                result = self._get_result_from_cursor()
                self.disconnect()
                return result
            else:
                return False
        except:
            dblog.dbtools_logger.error(f'Price getting failed: {sys.exc_info()[0:2]}')
            dblog.dbtools_logger.debug(f'Data_Getter.get_avg_price() was executed with args: \n'
                                       f'item = {item}\n'
                                       f'count = {count}')

    def get_prices(self, item):
        try:
            self._round5_mileage(item)
            self.connect()
            tabname = self._get_tabname(item)
            if tabname:
                self.cursor.execute(f'SELECT prices FROM "{tabname}" '
                                        f'WHERE kmage = \'{item["kmage"]}\' '
                                        f'AND year = \'{item["year"]}\' '
                                        f'ORDER BY id DESC '
                                        f'LIMIT 1 ')
                result = self.cursor.fetchone()[0]
                self.disconnect()
                return result
            else:
                return False
        except:
            dblog.dbtools_logger.error(f'Prices getting failed: {sys.exc_info()[0:2]}')
            dblog.dbtools_logger.debug(f'Data_Getter.get_prices() was executed with args: \n'
                                       f'item = {item}')

    def get_points(self, item):
        try:
            avg_price = self.get_avg_price(item, count=1)
            prices = self.get_prices(item)
            counters = [0 for _ in range(6)]
            counters[0] = avg_price
            for price in prices:
                if price < 0.8*avg_price:
                    counters[1] += 1
                elif 0.8*avg_price <= price < 0.95*avg_price:
                    counters[2] += 1
                elif 0.95*avg_price <= price <= 1.05*avg_price:
                    counters[3] += 1
                elif 1.05*avg_price < price <= 1.2*avg_price:
                    counters[4] += 1
                else:
                    counters[5] += 1
            return counters
        except:
            dblog.dbtools_logger.error(f'Gist data getting failed: {sys.exc_info()[0:2]}')
            dblog.dbtools_logger.debug(f'Data_Getter.get_points() was executed with args: \n'
                                       f'item = {item}')
