
from connection import GetConnection
import bcrypt
import datetime
from datetime import timedelta

def userExist(username):
    con = GetConnection()
    cursor = con.cursor()
    sqlite_insert_with_param = "SELECT id FROM users where username = :username ;"
    cursor.execute(sqlite_insert_with_param, {"username":username})
    rows = cursor.fetchall()
    length = len(rows)
    cursor.close()
    if length == 0:
        return False
    else:
        return True
    

def CreateUser(username,password,email):

    hashval = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = (username,hashval,email,datetime.datetime.utcnow())
    con = GetConnection()
    cursor = con.cursor()
    sqlite_insert_with_param = "INSERT INTO users (username,password,email,date) VALUES(?, ?, ?, ?)"
    cursor.execute(sqlite_insert_with_param, user)
    con.commit()
    print(cursor.lastrowid)
    cursor.close()
    return True

def PasswordMatchesForUser(username,password):
    con = GetConnection()
    cursor = con.cursor()
    sqlite_insert_with_param = "SELECT password FROM users where username = :username ;"
    cursor.execute(sqlite_insert_with_param, {"username":username})
    rows = cursor.fetchall()
    length = len(rows)
    if(length > 0):
        hashed = rows[0][0]
        if bcrypt.checkpw(password.encode('utf-8'), hashed):
            return True
   
    return False