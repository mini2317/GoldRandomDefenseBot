from discord.ext import tasks, commands
from discord.ui import View, Button, Select
from discord import Interaction, ButtonStyle
from emoji import core
import discord, sqlite3, os, asyncio, random, datetime, json

DATABASE_PATH = os.path.join('.','data','users.db')
USER_MASTER = "UserMaster"
TOKEN_PATH = os.path.join('.','data','token.txt')
FHBT_IMAGE = "https://media.discordapp.net/attachments/1175423530054201364/1177105955545153636/face-holding-back-tears.png?ex=65714c59&is=655ed759&hm=ca7484f164beebf32a17f252fd430b5c1df05731899379ecff0fe92bfcb2f738&=&format=webp&width=360&height=360"
bot = commands.Bot(command_prefix='ㄱ', intents = discord.Intents.all())
bot.remove_command('help')
with open(TOKEN_PATH, 'r', encoding = "UTF-8") as file:
    token = file.read()

con = sqlite3.connect(DATABASE_PATH)
cur = con.cursor()
tableExist = cur.execute(f"SELECT name FROM sqlite_master WHERE type='table';").fetchall()
if not any(map(lambda x : x[0] == USER_MASTER or USER_MASTER == f"'{x[0]}'", tableExist)):
    cur.execute(f'''CREATE TABLE {USER_MASTER} (userId INT, handling TEXT)''')
con.commit()
con.close()

def randomColor(): return random.randint(0, 255) * 256 * 256 + random.randint(0, 255) * 256 + random.randint(0, 255)
def todayStamp(): return 'D'+datetime.date.today().isoformat().replace(*"-_")
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
        VALUES ({userId}, {handling})
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

class RegisterUser(View):
    def __init__(self, ctx, arg):
        super().__init__()
        self.ctx = ctx
        self.arg = arg
        self.disabled = False
    
    @discord.ui.button(label = "확인", style = discord.ButtonStyle.primary, emoji = "✅")
    async def ok(self, interaction, button):
        user = self.ctx.author
        if self.disabled or (not interaction.user.id == user.id):
            return
        self.disabled = True
        embed = discord.Embed(
            title = "✅ 가입 완료 ✅",
            description = '가입 성공! 응원하겠습니다!',
            color = discord.Color.green()
        )
        self.callback = await interaction.response.send_message(embed = embed)

class DeleteUser(View):
    def __init__(self, ctx, arg):
        super().__init__()
        self.ctx = ctx
        self.arg = arg
        self.disabled = False
    
    @discord.ui.button(label = "확인", style = discord.ButtonStyle.primary, emoji = "✅")
    async def ok(self, interaction, button):
        user = self.ctx.message.author
        if self.disabled or (not interaction.user.id == user.id):
            return
        self.disabled = True
        deleteUser(user.id)
        embed = discord.Embed(
            title = "✅ 탈퇴 성공",
            description = '탈퇴에 성공하였습니다!',
            color = discord.Color.green()
        )
        self.callback = await interaction.response.send_message(embed = embed)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    if not alertEveryday.is_running():
        alertEveryday.start()
    await bot.change_presence(activity = discord.Game(name = "ㄱ도움"))

@bot.command()
async def 핑(ctx):
    await ctx.send(f'``{bot.latency * 1000}ms``')

@bot.command(name = "도움")
async def 도움(ctx, *arg):
    embed = discord.Embed(title = "도움 <:fhbt:1159345785528385606>", color = 0x18c0e2)
    embed.add_field(name = "가입", value = "가입해서 매일 나오는 문제들을 풀어보세요!", inline = False)
    embed.add_field(name = "탈퇴", value = "탈퇴하여 더 이상 문제들을 받지 않습니다.", inline = False)
    await ctx.send(embed = embed)

@bot.command(name = "가입")
async def 가입(ctx, *arg):
    if not arg: 
        embed = discord.Embed(title = f"가입 커맨드 사용법", description = "ㄱ가입 <solved.ac 핸들링>", color = 0xffbf00)
        await ctx.send(embed = embed)
        return
    if not getUser(ctx.author.id):
        embed = discord.Embed(
            title = f"🔔 가입 🔔",
            description = "가입해서 매일 나오는 무작위 문제들을 풀어보세요!",
            color = 0xffbf00
        )
        await ctx.send(embed = embed, view = RegisterUser(ctx, arg))
    else:
        embed = discord.Embed(
            title = "⚠️ 가입 실패 ⚠️",
            description='등록되지 않은 유저입니다!',
            color = 0xed2b2a
        )
        await ctx.send(embed = embed)

@bot.command(name = "탈퇴")
async def 탈퇴(ctx, *arg):
    if getUser(ctx.author.id):
        embed = discord.Embed(
            title = f"🔔 탈퇴 🔔",
            description = "탈퇴해서 문제를 더 이상 받지 않습니다.",
            color = 0xffbf00
        )
        await ctx.send(embed = embed, view = DeleteUser(ctx, arg))
    else:
        embed = discord.Embed(
            title = "⚠️ 탈퇴 실패 ⚠️",
            description='가입되어 있지 않습니다.',
            color = discord.Color.red()
        )
        await ctx.send(embed = embed)

@tasks.loop(seconds = 1)
async def alertEveryday():
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute
    second = now.second
    tester = second % 3 == 0
    if second + minute + hour == 0:
        yesterday = now - datetime.timedelta(days = 1)        
    if second  == -1:
        pass
bot.run(token)