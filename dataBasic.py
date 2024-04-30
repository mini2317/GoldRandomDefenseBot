import os, sqlite3, requests, json, random
from problemRequest import *
from enum import Enum

DATABASE_PATH = os.path.join('.','data','data.db')
USER_MASTER = "UserMaster"
GUILD_MASTER = "GuildMaster"
PROBLEM_LOCAL_SRC = "ProblemLocalSource"
PROBLEMS_JSON_PATH = os.path.join('.','data','problems.json')
TOKEN_PATH = os.path.join('.','data','token.txt')
BOT_ADMINS_ID_PATH = os.path.join('.','data','botAdminsId.txt')

GOLD_COLOR = 0xec9a00
GOLD_5_IMAGE = "https://media.discordapp.net/attachments/1175423530054201364/1234465905854120016/11.png?ex=6630d577&is=662f83f7&hm=021e5322d9965a3929696a1347d0d1312962099f4d342da3db84d4ed9f04f075&=&format=webp&quality=lossless&width=600&height=768"
GOLD_4_IMAGE = "https://media.discordapp.net/attachments/1175423530054201364/1234465906071961641/12.png?ex=6630d577&is=662f83f7&hm=409b10d43449679465ed815809bc2c9ba7e07782e78247d1e121bf3c96feb951&=&format=webp&quality=lossless&width=600&height=768"
GOLD_3_IMAGE = "https://media.discordapp.net/attachments/1175423530054201364/1234465906269225052/13.png?ex=6630d577&is=662f83f7&hm=5ffaff84f3ed31864a53a285f71f7545debecd20d5e8d7981f4f42a3e1f9e2c4&=&format=webp&quality=lossless&width=600&height=768"
GOLD_2_IMAGE = "https://media.discordapp.net/attachments/1175423530054201364/1234465906500042782/14.png?ex=6630d577&is=662f83f7&hm=2c1086b6f9ea1d494f45d488cec340845395c1b3a2220a4747a3ed4d41d040dd&=&format=webp&quality=lossless&width=600&height=768"
GOLD_1_IMAGE = "https://media.discordapp.net/attachments/1175423530054201364/1234465906722078742/15.png?ex=6630d577&is=662f83f7&hm=ee42b9ef6438bf38b899709a5c9cfc6a7ac7f807fa054d034031657368510417&=&format=webp&quality=lossless&width=600&height=768"

GOLD_IMAGE = [
    GOLD_1_IMAGE,
    GOLD_2_IMAGE,
    GOLD_3_IMAGE,
    GOLD_4_IMAGE,
    GOLD_5_IMAGE
]

class UserDataIdx(Enum):
    userId = 0
    handling = 1
    streak = 2
    longestStreak = 3
    gold = 4
    solvedCnt = 5

class GuildDataIdx(Enum):
    guildId = 0
    channelId = 1
    canNotion = 2

FHBT_IMAGE = "https://media.discordapp.net/attachments/1175423530054201364/1177105955545153636/face-holding-back-tears.png?ex=65714c59&is=655ed759&hm=ca7484f164beebf32a17f252fd430b5c1df05731899379ecff0fe92bfcb2f738&=&format=webp&width=360&height=360"

with open(TOKEN_PATH, 'r', encoding = "UTF-8") as file:
    TOKEN = file.read()

with open(BOT_ADMINS_ID_PATH, 'r', encoding = "UTF-8") as file:
    BOT_ADMINS_ID = tuple(map(int, file.read().split("\n")))

def getFromJson(jsonFilePath):
    with open(jsonFilePath, 'r', encoding = "UTF-8") as file: 
        loadedJson = json.loads(file.read())
    return loadedJson

def addToJson(jsonFilePath, *contents):
    with open(jsonFilePath, 'r', encoding = "UTF-8") as file: 
        loadedJson = json.loads(file.read())
    loadedJson += contents
    with open(jsonFilePath, 'w', encoding = "UTF-8") as file: 
        file.write(json.dumps(loadedJson))

def popJson(jsonFilePath, idx):
    with open(jsonFilePath, 'r', encoding = "UTF-8") as file: 
        loadedJson = json.loads(file.read())
    rst = loadedJson.pop(idx)
    with open(jsonFilePath, 'w', encoding = "UTF-8") as file:
        file.write(json.dumps(loadedJson))
    return rst

def dropEveryDataBases():
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    tableExist = cur.execute(f"SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    for table in map(lambda x : x[0], tableExist):
        cur.execute(f"DROP TABLE '{table}'")
    con.commit()
    con.close()

def initializeDataBase():
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    tableExist = cur.execute(f"SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    if not any(map(lambda x : x[0] == USER_MASTER or USER_MASTER == f"'{x[0]}'", tableExist)):
        cur.execute(f'''CREATE TABLE {USER_MASTER} (userId INT, handling TEXT, streak INT, longestStreak INT, gold INT, solvedCnt INT)''')
    if not any(map(lambda x : x[0] == GUILD_MASTER or GUILD_MASTER == f"'{x[0]}'", tableExist)):
        cur.execute(f'''CREATE TABLE {GUILD_MASTER} (guildId INT, channelId INT, canNotion INT)''')
    if not any(map(lambda x : x[0] == PROBLEM_LOCAL_SRC or PROBLEM_LOCAL_SRC == f"'{x[0]}'", tableExist)):
        cur.execute(f'''CREATE TABLE {PROBLEM_LOCAL_SRC} (problemId INT)''')
    con.commit()
    con.close()