import random, datetime

def randomColor():
    return random.randint(0, 255) * 256 * 256 + random.randint(0, 255) * 256 + random.randint(0, 255)

def todayStamp():
    return 'D' + datetime.date.today().isoformat().replace(*"-_")

def getRandomGoldProblem():
    return