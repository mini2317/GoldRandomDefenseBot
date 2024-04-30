import requests, json
class User:
    def __init__(self, handle : int):
        self.handle = handle
        response = requests.get(f"https://solved.ac/api/v3/user/show?handle={handle}")
        if response.text != "Not Found":
            self.info = json.loads(response.text)
        else:
            self.info = None
    
    def __call__(self, key):
        if self.info is None:
            return None
        else:
            return self.info[key]

def IsExistHandle(handle):
    response = requests.get(f"https://solved.ac/api/v3/user/show?handle={handle}")
    return response.text != "Not Found"