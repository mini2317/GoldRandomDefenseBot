import requests, json
class Problem:
    def __init__(self, problemId : int):
        self.problemId = problemId
        response = requests.get(f"https://solved.ac/api/v3/search/problem?query=id:{self.problemId}&direction=asc&sort=id")
        self.info = json.loads(response.text)['items'][0]
    
    def __call__(self, key):
        return self.info[key]