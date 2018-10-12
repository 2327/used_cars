from api import common

@api.route('/users')
def get_users():
    return common.get_users()
