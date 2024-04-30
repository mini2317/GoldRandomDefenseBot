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
        ''').fetchall()
        con.commit()
        con.close()
        if search:
            return search[0]
        else:
            return False
    
    @staticmethod
    def add(userId, handle):
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        cur.execute(f'''
            INSERT
            INTO "{USER_MASTER}" (userId, handle, streak, longestStreak, gold, solvedCnt)
            VALUES ("{userId}", "{handle}", 0, 0, 0, 0)
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
        cur.execute(f'''
            UPDATE "{USER_MASTER}"
            SET solvedCnt = {user[UserDataIdx.solvedCnt] + 1}
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
            SET gold = {user[UserDataIdx.gold] + amount}
            WHERE userId = '{userId}'
        ''')
        con.commit()
        con.close()
    
    @staticmethod
    def addRewardGold(userId):
        user = UserData.get(userId)
        amount = getFromJson(PROBLEM_OF_TODAY_JSON_PATH)["level"] + max(0, min(5, user[UserDataIdx.streak] - 3))
        UserData.addGold(userId, amount)
        return amount

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
            if checkUserSolved(user[UserDataIdx.handle], problemId):
                UserData.addRewardGold(user[UserDataIdx.userId])
                UserData.updateStreak(user[UserDataIdx.userId])
            else:
                UserData.resetStreak(user[UserDataIdx.userId])