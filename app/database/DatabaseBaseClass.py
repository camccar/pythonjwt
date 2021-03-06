
import psycopg2
import datetime
from datetime import date
import sqlite3
import os
from pathlib import Path


#Meant to be the interface class
class DatabaseBaseClass:
    def InitUserTable(self):
        print("Initializing User Table")

    def InitUserDatabase(self):
        print("Initializing user Database")

    def InitializeDatabase(self):
        print("Initilizing Database")
        self.InitUserDatabase()
        self.InitUserTable()

    def SaveNewUser(self):
        print("Saving user")

    def UserExist(self,username:str)->bool:
        print("Checking user exist")
        return False
    
    def GetPasswordForUser(self,username:str)->str:
        print("Getting password for user")
        return ""
    
    def CreateUser(self):
        print("Creating user")
    
    def GetUserForUserName(self,username)-> map:
        print("Getting user")
    
        

class DatabaseSQLLite(DatabaseBaseClass):
    def InitUserTable(self):
        super().InitUserTable()
        print("initilising Lite Table Class")
        con = self.GetConnection()
        cursor = con.cursor()
        Query = "SELECT name FROM sqlite_master where type = 'table' AND name NOT LIKE 'SQLITE_%';"
        cursor.execute(Query)
        rows = cursor.fetchall()
        UsersFound = False
        tokensFound = False
        for row in rows:
            if row[0] == 'users':
                UsersFound = True
            if row[0] == 'tokens':
                tokensFound = True
            
        if not UsersFound:
            fd = open('app/sqlfiles/CREATEUSERTABLESQLITE.sql', 'r')
            sqlFile = fd.read()
            cursor.execute(sqlFile)

        if not tokensFound:
            fd = open('app/sqlfiles/CREATETOKENTABLESQLITE.sql', 'r')
            sqlFile = fd.read()
            cursor.execute(sqlFile)
        
        con.commit()
        cursor.close()

    def InitUserDatabase(self):
        super().InitUserDatabase()
        print("initilising Lite user database")
        my_file = Path("user.db")

        if not my_file.is_file():
            #Open and close db file
            con = sqlite3.connect('users.db')
            c = con.cursor()
            con.commit()
            c.close()
        

    def GetConnection(self):
        con = sqlite3.connect('users.db')
        return con

    def CreateUser(self,username:str,HashedPassword:str,email:str):
        super().CreateUser()
        user = (username,HashedPassword,email,datetime.datetime.utcnow())
        con = self.GetConnection()
        cursor = con.cursor()
        sqlite_insert_with_param = "INSERT INTO users (username,password,email,CreateDate) VALUES(?, ?, ?, ?)"
        cursor.execute(sqlite_insert_with_param, user)
        con.commit()
        cursor.close()
        return True

    def UserExist(self,username:str)->bool:
        con = self.GetConnection()
        cursor = con.cursor()
        Query = "SELECT username FROM users where username = ?"
        cursor.execute(Query,(username,))
        rows = cursor.fetchall()
        UserFound = False
        print(rows)
        for row in rows:
            if row[0] == username:
                UserFound = True

        return UserFound

    def GetPasswordForUser(self,username:str)->str:
        super().GetPasswordForUser(username)
        con = self.GetConnection()
        cursor = con.cursor()
        Query = "SELECT password FROM users where username = ?"
        cursor.execute(Query,(username,))
        rows = cursor.fetchone()
        print(rows)
        retVal = rows[0]
        cursor.close()
        return retVal

    def GetUserForUserName(self,username)-> map:
        super().GetUserForUserName(username)
        con = self.GetConnection()
        cursor = con.cursor()
        sqlite_get_with_param = "SELECT id,email FROM users where username = :username ;"
        cursor.execute(sqlite_get_with_param, {"username":username})
        rows = cursor.fetchall()
        length = len(rows)
        user = {"id":0,"username":"","email":""}
        if(length > 0):
            user["id"] = rows[0][0]
            user["username"] = username
            user["email"] = rows[0][1]
        cursor.close()
        return user

class DatabasePostGres(DatabaseBaseClass):
    def __init__(self):
        
        self.db = os.environ['DATABASE']
        self.user = os.environ['PGUSERNAME']
        self.password = os.environ['PGPASSWORD']
        self.host = os.environ['POSTGRESURL']
        self.port = os.environ['PGPORT']

    def GetConnection(self):
        return psycopg2.connect(database=self.db, user=self.user, password=self.password, host=self.host, port=self.port)

    def CreateUser(self,username:str,HashedPassword:str,email:str):
        super().CreateUser()
        user = (username,HashedPassword.decode('ascii'),email,datetime.datetime.utcnow())
        con = self.GetConnection()
        cursor = con.cursor()
        insert_with_param_query = "INSERT INTO users (username,password,email,createdate) VALUES(%s, %s, %s, %s)"
        cursor.execute(insert_with_param_query, user)
        con.commit()
        cursor.close()
        return True

    def UserExist(self,username:str)->bool:
        con = self.GetConnection()
        cursor = con.cursor()
        Query = "SELECT username FROM users where username = %s"
        cursor.execute(Query,(username,))
        rows = cursor.fetchall()
        UserFound = False
        print(rows)
        for row in rows:
            if row[0] == username:
                UserFound = True
        return UserFound

    def GetUserForUserName(self,username)-> map:
        super().GetUserForUserName(username)
        con = self.GetConnection()
        cursor = con.cursor()
        Query = "SELECT id,email FROM users where username = %s"
        cursor.execute(Query, (username,))
        rows = cursor.fetchall()
        length = len(rows)
        user = {"id":0,"username":"","email":""}
        if(length > 0):
            user["id"] = rows[0][0]
            user["username"] = username
            user["email"] = rows[0][1]
        cursor.close()
        return user


    def InitUserTable(self):
        super().InitUserTable()
        print("inituser tables")
        con = psycopg2.connect(database=self.db, user=self.user, password=self.password, host=self.host, port=self.port)
        cur = con.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        rows = cur.fetchall()
        userTableFound = False
        tokensFound = False
        for row in rows:
            print(row[0])
            if row[0] == "users":
                 userTableFound = True
            if row[0] == "tokens":
                 tokensFound = True
        
        if not userTableFound:
            print("creating users table")
            fd = open('app/sqlfiles/CREATEUSERSTABLE.sql', 'r')
            sqlFile = fd.read()
            cur.execute(sqlFile)
        
        if not tokensFound:
            print("creating tokens table")
            fd = open('app/sqlfiles/CREATETOKENTABLEPOSTGRES.sql', 'r')
            sqlFile = fd.read()
            cur.execute(sqlFile)

        con.commit()
        con.close()

    def GetPasswordForUser(self,username:str)->str:
        super().GetPasswordForUser(username)
        con = self.GetConnection()
        cursor = con.cursor()
        Query = "SELECT password FROM users where username = %s"
        cursor.execute(Query,(username,))
        rows = cursor.fetchone()
        return rows[0].encode('utf-8')

    def InitUserDatabase(self):
        super().InitUserDatabase()
        con = psycopg2.connect(database="postgres", user=self.user, password=self.password, host=self.host, port=self.port)
        con.autocommit = True
        cur = con.cursor()
        cur.execute("SELECT datname FROM pg_database")
        rows = cur.fetchall()
        userdatabaseFound = False
        for row in rows:
            if row[0] == "userdatabase":
                userdatabaseFound = True
        
        if not userdatabaseFound:
            print("Creating user database")
            cur.execute("CREATE DATABASE userdatabase")


        con.close()


class DatabaseFactory:
    def GetDataBase(self):
        if os.environ['DATABASETYPE'] == "POSTGRES":
            d = DatabasePostGres()
            return d
        else:
            d = DatabaseSQLLite()
        return d

