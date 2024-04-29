import os, sqlite3, requests, json, random

DATABASE_PATH = os.path.join('.','data','data.db')
USER_MASTER = "UserMaster"
GUILD_MASTER = "GuildMaster"
PROBLEM_LOCAL_SRC = "ProblemLocalSource"
PROBLEMS_JSON_PATH = os.path.join('.','data','problems.json')
TOKEN_PATH = os.path.join('.','data','token.txt')
BOT_OWNERS_ID_PATH = os.path.join('.','data','botOwnerId.txt')

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

FHBT_IMAGE = "https://media.discordapp.net/attachments/1175423530054201364/1177105955545153636/face-holding-back-tears.png?ex=65714c59&is=655ed759&hm=ca7484f164beebf32a17f252fd430b5c1df05731899379ecff0fe92bfcb2f738&=&format=webp&width=360&height=360"

with open(TOKEN_PATH, 'r', encoding = "UTF-8") as file:
    TOKEN = file.read()

with open(BOT_OWNERS_ID_PATH, 'r', encoding = "UTF-8") as file:
    BOT_OWNERS_ID = tuple(map(int, file.read().split("\n")))

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

def initializeDataBase():
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    tableExist = cur.execute(f"SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    if not any(map(lambda x : x[0] == USER_MASTER or USER_MASTER == f"'{x[0]}'", tableExist)):
        cur.execute(f'''CREATE TABLE {USER_MASTER} (userId INT, handling TEXT)''')
    if not any(map(lambda x : x[0] == GUILD_MASTER or GUILD_MASTER == f"'{x[0]}'", tableExist)):
        cur.execute(f'''CREATE TABLE {GUILD_MASTER} (guildId INT, channelId INT, canNotion INT)''')
    if not any(map(lambda x : x[0] == PROBLEM_LOCAL_SRC or PROBLEM_LOCAL_SRC == f"'{x[0]}'", tableExist)):
        cur.execute(f'''CREATE TABLE {PROBLEM_LOCAL_SRC} (problemId INT, problemTier INT)''')
    con.commit()
    con.close()

def getUser(userId):
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
    ''').fetchall()
    con.commit()
    con.close()
    return search

def addGuild(guildId, channelId):
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute(f'''
        INSERT
        INTO "{GUILD_MASTER}" (guildId, channelId, canNotion)
        VALUES ("{guildId}", "{channelId}", 1)
    ''')
    con.commit()
    con.close()

def changeGuildNotionChannel(guildId, channelId):
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute(f'''
        UPDATE "{GUILD_MASTER}"
        SET channelId = {channelId}
        WHERE guildId = '{guildId}'
    ''')
    con.commit()
    con.close()

def turnOnGuildNotion(guildId):
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute(f'''
        UPDATE "{GUILD_MASTER}"
        SET canNotion = 1
        WHERE guildId = '{guildId}'
    ''')
    con.commit()
    con.close()

def turnOffGuildNotion(guildId):
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute(f'''
        UPDATE "{GUILD_MASTER}"
        SET canNotion = 0
        WHERE guildId = '{guildId}'
    ''')
    con.commit()
    con.close()

def renewOriginalProblems():
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute(f'''
        DROP TABLE "{PROBLEM_LOCAL_SRC}";
    ''')
    con.commit()
    con.close()
    initializeDataBase()
    updateProblems()
    renewProblems()

def renewProblems():
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    localProblemIds = list(map(lambda x: (x[0], x[1]), cur.execute(f'''
        SELECT *
        FROM "{PROBLEM_LOCAL_SRC}"
    ''').fetchall()))
    con.commit()
    con.close()
    with open(PROBLEMS_JSON_PATH, 'w', encoding = "UTF-8") as file: 
        file.write(json.dumps(localProblemIds))

def updateProblems():
    response = requests.get("https://solved.ac/api/v3/search/problem?query=*g&direction=asc&sort=id")
    siteProblemCnt = json.loads(response.text)['count']
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    localProblemCnt = len(cur.execute(f'''
        SELECT *
        FROM "{PROBLEM_LOCAL_SRC}"
    ''').fetchall())
    if localProblemCnt == siteProblemCnt:
        con.commit()
        con.close()
        return
    tmp = []
    for i in range(localProblemCnt, siteProblemCnt):
        if i % 50 == 0:
            print(f'데이터 로드 : {i / siteProblemCnt * 100} % 완료')
            if i == 0:
                response = requests.get(f"https://solved.ac/api/v3/search/problem?query=*g&direction=asc&sort=id")
            else:
                response = requests.get(f"https://solved.ac/api/v3/search/problem?query=*g&direction=asc&page={i // 50}&sort=id")
            siteProblems = json.loads(response.text)["items"]
        cur.execute(f'''
            INSERT
            INTO "{PROBLEM_LOCAL_SRC}" (problemId, problemTier)
            VALUES ({siteProblems[i % 50]["problemId"]}, {15 - siteProblems[i % 50]["level"]})
        ''').fetchall()
        tmp.append((siteProblems[i % 50]["problemId"], 15 - siteProblems[i % 50]["level"]))
    addToJson(PROBLEMS_JSON_PATH, *tmp)
    con.commit()
    con.close()

def getRandomProblem():
    updateProblems()
    problems = getFromJson(PROBLEMS_JSON_PATH)
    idx = random.randint(0, len(problems))
    problem, tier = popJson(PROBLEMS_JSON_PATH, idx)
    if len(problems) == 1:
        renewProblems()
    print(len(problems) - 1)
    return (problem, tier)