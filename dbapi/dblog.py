from logging import Logger, Formatter, FileHandler
from os import path


log_file_path = path.join(path.dirname(path.abspath(__file__)), 'dbtools_log.txt')

dbtools_logger = Logger('dbtools')

fmt = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'
dbtools_err_formatter = Formatter(fmt)

dbtools_err_handler = FileHandler(log_file_path)
dbtools_err_handler.setLevel('ERROR')
dbtools_err_handler.setFormatter(dbtools_err_formatter)

dbtools_logger.addHandler(dbtools_err_handler)


def log(message):        #mock for logging func
    print(message)
