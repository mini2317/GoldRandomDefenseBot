from dataBasic import *
import random

class ProblemData:
    @staticmethod
    def remakeDatabaseTable():
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        cur.execute(f'''
            DROP TABLE "{PROBLEM_LOCAL_SRC}";
        ''')
        con.commit()
        con.close()
        initializeDataBase()
        ProblemData.update()
        ProblemData.refillJson()

    @staticmethod
    def refillJson():
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        localProblemIds = list(map(lambda x: x[0], cur.execute(f'''
            SELECT *
            FROM "{PROBLEM_LOCAL_SRC}"
        ''').fetchall()))
        con.commit()
        con.close()
        with open(PROBLEMS_JSON_PATH, 'w', encoding = "UTF-8") as file: 
            file.write(json.dumps(localProblemIds))

    @staticmethod
    def deleteById(problemId):
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        cur.execute(f'''
            DELETE FROM "{PROBLEM_LOCAL_SRC}"
            WHERE problemId = "{problemId}";
        ''')
        con.commit()
        con.close()

    @staticmethod
    def update(onlyEditTable = False):
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
        siteProblems = dict()
        for i in range(localProblemCnt, siteProblemCnt):
            if i % 50 == 0:
                print(f'데이터 로드 : {(i - localProblemCnt) / (siteProblemCnt - localProblemCnt) * 100} % ({i} / {siteProblemCnt - localProblemCnt}) 완료')
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
            if not onlyEditTable:
                tmp.append(siteProblems[i % 50]["problemId"])
        if siteProblemCnt % 50 != 0:
            print(f'데이터 로드 : 100.0 % ({siteProblemCnt - localProblemCnt} / {siteProblemCnt - localProblemCnt}) 완료')
        if not onlyEditTable:
            addToJson(PROBLEMS_JSON_PATH, *tmp)
        con.commit()
        con.close()

    @staticmethod
    def popRandomProblem():
        ProblemData.update()
        while True:
            problems = getFromJson(PROBLEMS_JSON_PATH)
            idx = random.randint(0, len(problems))
            problemId = popJson(PROBLEMS_JSON_PATH, idx)
            if len(problems) == 1:
                ProblemData.refillJson()
            problem = Problem(problemId)
            if 11 <= problem("level") <= 15:
                break
            else:
                ProblemData.deleteById(problemId)
        return problem
