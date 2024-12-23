import pymysql
class Database:
  def __init__(self):
    pymysql.connect(
      host="localhost",
      user="minha",
      password="q1w2e3",
      database="gcode_db",
      cursorclass=pymysql.cursors.DictCursor
    )