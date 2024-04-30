import requests, json
class User:
    def __init__(self, handle : int):
        self.handle = handle
        response = requests.get(f"https://solved.ac/api/v3/search/problem?query=id:{self.handle}&direction=asc&sort=id")
        if response.text:
            self.info = json.loads(response.text)
        else:
            self.info = None
    
    def __call__(self, key):
        if self.info is None:
            return None
        else:
            return self.info[key]

def checkExistHandle(handle):
    response = requests.get(f"https://solved.ac/api/v3/user/show?handle={handle}")
    return bool(json.loads(response.text)['count'])