import os, sqlite3, requests, json, random

DATABASE_PATH = os.path.join('.','data','data.db')
USER_MASTER = "UserMaster"
GUILD_MASTER = "GuildMaster"
PROBLEM_LOCAL_SRC = "ProblemLocalSource"
PROBLEMS_JSON_PATH = os.path.join('.','data','problems.json')

TOKEN_PATH = os.path.join('.','data','token.txt')
FHBT_IMAGE = "https://media.discordapp.net/attachments/1175423530054201364/1177105955545153636/face-holding-back-tears.png?ex=65714c59&is=655ed759&hm=ca7484f164beebf32a17f252fd430b5c1df05731899379ecff0fe92bfcb2f738&=&format=webp&width=360&height=360"

with open(TOKEN_PATH, 'r', encoding = "UTF-8") as file:
    TOKEN = file.read()

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
        cur.execute(f'''CREATE TABLE {PROBLEM_LOCAL_SRC} (problemId INT)''')
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
    ''').fetchall()[0]
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

def renewProblems():
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute(f'''
        DELETE
        FROM {PROBLEM_LOCAL_SRC}
    ''')
    con.commit()
    con.close()
    updateProblems()

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
            INTO "{PROBLEM_LOCAL_SRC}" (problemId)
            VALUES ({siteProblems[i % 50]["problemId"]})
        ''').fetchall()
        tmp.append(siteProblems[i % 50]["problemId"])
    addToJson(PROBLEMS_JSON_PATH, *tmp)
    con.commit()
    con.close()

def getRandomProblem():
    updateProblems()
    problems = getFromJson(PROBLEMS_JSON_PATH)
    idx = random.randint(0, len(problems))
    problem = popJson(PROBLEMS_JSON_PATH, idx)
    if len(problems) == 1:
        renewProblems()
    print(len(problems) - 1)
    return (idx, problem)