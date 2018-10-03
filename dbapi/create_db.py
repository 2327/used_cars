"""You should use this script to create used cars database. You can change DB settings in dbcfg.py
To execute script just open terminal in used_cars directory and enter "python -m dbapi.create_db" command.
Requirements: psycopg2 module have to be installed!
You can check error log in dbtools_log.txt"""


from .dbtools import Base_Creator


if __name__ == '__main__':
    with Base_Creator() as creator:
        creator.create_all()
