from dbtools import Base_Creator


if __name__ == '__main__':
    with Base_Creator() as creator:
        creator.create_all()
