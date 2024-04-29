import os, sqlite3

DATABASE_PATH = os.path.join('.','data','users.db')
USER_MASTER = "UserMaster"
GUILD_MASTER = "GuildMaster"
TOKEN_PATH = os.path.join('.','data','token.txt')
FHBT_IMAGE = "https://media.discordapp.net/attachments/1175423530054201364/1177105955545153636/face-holding-back-tears.png?ex=65714c59&is=655ed759&hm=ca7484f164beebf32a17f252fd430b5c1df05731899379ecff0fe92bfcb2f738&=&format=webp&width=360&height=360"

with open(TOKEN_PATH, 'r', encoding = "UTF-8") as file:
    TOKEN = file.read()

def initializeDataBase():
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    tableExist = cur.execute(f"SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    if not any(map(lambda x : x[0] == USER_MASTER or USER_MASTER == f"'{x[0]}'", tableExist)):
        cur.execute(f'''CREATE TABLE {USER_MASTER} (userId INT, handling TEXT)''')
    if not any(map(lambda x : x[0] == GUILD_MASTER or GUILD_MASTER == f"'{x[0]}'", tableExist)):
        cur.execute(f'''CREATE TABLE {GUILD_MASTER} (guildId INT, channelId INT, canNotion INT)''')
    con.commit()
    con.close()

def getUser(userId):
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    search = cur.execute(f'''
        SELECT *
        FROM "{USER_MASTER}"
        WHERE userId = {userId};
    ''').fetchall()
    con.commit()
    con.close()
    return search

def addUser(userId, handling):
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute(f'''
        INSERT
        INTO "{USER_MASTER}" (userId, handling)
        VALUES ("{userId}", "{handling}")
    ''')
    con.commit()
    con.close()

def deleteUser(userId):
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute(f'''
        DELETE
        FROM "{USER_MASTER}"
        WHERE userId = {userId}
    ''')
    con.commit()
    con.close()

def getGuild(guildId):
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    search = cur.execute(f'''
        SELECT *
        FROM "{GUILD_MASTER}"
        WHERE guildId = {guildId};
    ''').fetchall()[0]
    con.commit()
    con.close()
    return search

def addGuild(guildId, channelId):
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute(f'''
        INSERT
        INTO "{GUILD_MASTER}" (guildId, channelId)
        VALUES ("{guildId}", "{channelId}")
    ''')
    con.commit()
    con.close()

def turnOnNotion(guildId):
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute(f'''
        INSERT
        INTO "{GUILD_MASTER}" (guildId)
        VALUES ("{guildId}")
    ''')
    con.commit()
    con.close()