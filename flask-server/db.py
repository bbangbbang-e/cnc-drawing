import pymysql

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="flask_user",
        password="q1w2e3",
        database="gcode_db",
        cursorclass=pymysql.cursors.DictCursor
    )