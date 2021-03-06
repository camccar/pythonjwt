import jwt
from app.connection import GetConnection
from app.users import User
from json import dumps
import datetime
from datetime import timedelta
from datetime import date
import os


def myconverter(o): # used to serialise datetime
    if isinstance(o, datetime.datetime):
        return o.__str__()

def CreateTokenForUser(usr: User):
    if usr.id == 0:
        return # don't make a token for an empty user
    userobj = usr.ToDict()
    timeNow = datetime.datetime.utcnow()
    expireTime = timeNow+datetime.timedelta(days=5) # set it to expire in 5 days
    userobj['time'] = dumps(timeNow,default=myconverter) # add a time stamp so each token is unique
    
    encoded_jwt = jwt.encode(userobj, os.environ['SECRET'], algorithm='HS256')
    row = (timeNow,expireTime,encoded_jwt.decode('utf-8'),usr.id)
    con = GetConnection()
    cursor = con.cursor()
    sqlite_insert_with_param = "INSERT INTO tokens (creationdate,expirationdate,token,userid) VALUES(?, ?, ?, ?)"
    cursor.execute(sqlite_insert_with_param, row)
    con.commit()
    rowid =  cursor.lastrowid
    cursor.close()
    return rowid

def GetUserFromToken(tok: str)-> User:
    usr = User()
    try:
        tokenObj = jwt.decode(tok, os.environ['SECRET'], algorithms=['HS256'])
    except:
        print("problem decoding token")
        return usr
    
    usr.id = tokenObj["id"]
    usr.username = tokenObj["username"]
    usr.email = tokenObj["email"]
    return usr

def GetTokenFromTokenId(tokid: str):
    con = GetConnection()
    cursor = con.cursor()
    sqlite_query = "SELECT token FROM tokens where id = :id ;"
    cursor.execute(sqlite_query, {"id":tokid})
    rows = cursor.fetchall()
    length = len(rows)
    retVal = ""
    if(length > 0):
        retVal = rows[0][0]

    return retVal


