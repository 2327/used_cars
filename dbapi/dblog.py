from logging import Logger, Formatter, FileHandler
from os import path


log_file_path = path.join(path.dirname(path.abspath(__file__)), 'dbtools_log.txt')
debug_log_path = path.join(path.dirname(path.abspath(__file__)), 'debug_log.txt')

dbtools_logger = Logger('dbtools')

fmt = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'
dbtools_err_formatter = Formatter(fmt)

dbtools_err_handler = FileHandler(log_file_path)
dbtools_err_handler.setLevel('ERROR')
dbtools_err_handler.setFormatter(dbtools_err_formatter)

dbtools_debug_handler = FileHandler(debug_log_path)
dbtools_debug_handler.setLevel('DEBUG')
dbtools_debug_handler.setFormatter(dbtools_err_formatter)

dbtools_logger.addHandler(dbtools_err_handler)
dbtools_logger.addHandler(dbtools_debug_handler)


def log(message):        #mock for logging func
    print(message)
