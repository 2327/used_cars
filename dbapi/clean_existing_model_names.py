"""You should use this script to clean existing model names in database. You can change DB settings in dbcfg.py
To execute script just open terminal in used_cars directory and enter "python -m dbapi.clean_existing_model_names" command.
Requirements: psycopg2 module have to be installed!
You can check error log in dbtools_log.txt"""

#dont working now, it needed to add checking and merging functional for tables with same names.


from .dbtools import Base_Updater


if __name__ == "__main__":
    updater = Base_Updater()
    updater.clean_existing_names()
