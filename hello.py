# from flask import Flask
# app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return 'Hello World!'

# if __name__ == '__main__':
#     app.run()

from sqlite3 import *
conn = connect('birthdays2.db')
db = conn.cursor()

#db.execute("INSERT INTO birthdays (name, month, day) VALUES (?, ?, ?)", (name, month, day))
#rows = db.execute("SELECT * FROM users WHERE username = (?)", (("Leah"), ))
rows = db.execute("SELECT username FROM users WHERE id = (?)", (int(1),)).fetchone()[0]
print(rows)

from datetime import date

today = date.today()
todayStr = str(today.month) + str(today.day)
print(todayStr)



