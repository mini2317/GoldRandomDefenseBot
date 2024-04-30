from dataBasic import *
class UserData:
    @staticmethod
    def getEveryUsers():
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        search = cur.execute(f'''
            SELECT *
            FROM "{USER_MASTER}";
        ''').fetchall()
        con.commit()
        con.close()
        return search
    
    @staticmethod
    def get(userId):
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        search = cur.execute(f'''
            SELECT *
            FROM "{USER_MASTER}"
            WHERE userId = {userId};
        ''').fetchall()[0]
        con.commit()
        con.close()
        return search
    
    @staticmethod
    def add(userId, handling):
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        cur.execute(f'''
            INSERT
            INTO "{USER_MASTER}" (userId, handling, streak, longestStreak, gold, solvedCnt)
            VALUES ("{userId}", "{handling}", 0, 0, 0, 0)
        ''')
        con.commit()
        con.close()
    
    @staticmethod
    def updateStreak(userId):
        user = UserData.get(userId)
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        cur.execute(f'''
            UPDATE "{USER_MASTER}"
            SET streak = {user[UserDataIdx.streak] + 1}
            WHERE userId = '{userId}'
        ''')
        if user[UserDataIdx.streak] + 1 > user[UserDataIdx.longestStreak]:
            cur.execute(f'''
                UPDATE "{USER_MASTER}"
                SET longestStreak = {user[UserDataIdx.streak] + 1}
                WHERE userId = '{userId}'
            ''')
        con.commit()
        con.close()
    
    @staticmethod
    def resetStreak(userId):
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        cur.execute(f'''
            UPDATE "{USER_MASTER}"
            SET streak = 0
            WHERE userId = '{userId}'
        ''')
        con.commit()
        con.close()
    
    @staticmethod
    def addGold(userId, amount):
        user = UserData.get(userId)
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        cur.execute(f'''
            UPDATE "{USER_MASTER}"
            SET streak = {user[UserDataIdx.gold] + amount}
            WHERE userId = '{userId}'
        ''')
        con.commit()
        con.close()
    
    @staticmethod
    def delete(userId):
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        cur.execute(f'''
            DELETE
            FROM "{USER_MASTER}"
            WHERE userId = {userId}
        ''')
        con.commit()
        con.close()
    
    @staticmethod   
    def updateUsersStreak(problemId):
        for user in UserData.getEveryUsers():
            if checkUserSolved(user[UserDataIdx.handling], problemId):
                UserData.updateStreak(user[UserDataIdx.userId])
            else:
                UserData.resetStreak(user[UserDataIdx.userId])