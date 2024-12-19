import pymysql

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="flask_user",
        password="your_password",
        database="gcode_db",
        cursorclass=pymysql.cursors.DictCursor
    )