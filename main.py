from discord.ext import tasks, commands
from discord.ui import View
import discord, datetime
from dataControl import *

bot = commands.Bot(command_prefix='ㄱ', intents = discord.Intents.all())
bot.remove_command('help')
initializeDataBase()

async def alertToGuilds(problemId, tier):
    for guild in bot.guilds:
        if not getGuild(guild.id):
            for channel in guild.channels:
                if channel.type == discord.ChannelType.text:
                    addGuild(guild.id, channel.id)
                    break
        if getGuild(guild.id)[0][2]:
            nowGuild = getGuild(guild.id)[0]
            testChannel = bot.get_guild(guild.id).get_channel(nowGuild[1])
            embed = discord.Embed(title = "오늘의 골드 문제입니다!", description = f"https://www.acmicpc.net/problem/{problemId}", color = GOLD_COLOR)
            embed.set_thumbnail(url = GOLD_IMAGE[tier])
            await testChannel.send(embed = embed)

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
        addUser(user.id, self.arg[0])
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
    for guild in bot.guilds:
        print(f'{guild.id} : {guild.name}')
    print('------')
    if not alertEveryday.is_running():
        alertEveryday.start()
    await bot.change_presence(activity = discord.Game(name = "ㄱ도움"))

@bot.command()
async def 핑(ctx):
    await ctx.send(f'``{bot.latency * 1000}ms``')

@bot.command()
async def 테스트(ctx):
    if ctx.author.id in BOT_OWNERS_ID:
        problemId, tier = getRandomProblem()
        await alertToGuilds(problemId, tier)

@bot.command()
async def 재구성(ctx):
    if ctx.author.id in BOT_OWNERS_ID:
        renewOriginalProblems()
        await ctx.send(f'``데이터베이스가 초기화 된 후 다시 업데이트되었습니다!``')

@bot.command()
async def 리필(ctx):
    if ctx.author.id in BOT_OWNERS_ID:
        renewProblems()
        await ctx.send(f'``json이 초기화 된 후 다시 업데이트되었습니다!``')

@bot.command(name = "도움")
async def 도움(ctx, *arg):
    embed = discord.Embed(title = "도움 <:fhbt:1159345785528385606>", color = 0x18c0e2)
    embed.add_field(name = "가입", value = "가입해서 매일 나오는 문제들을 풀어보세요!", inline = False)
    embed.add_field(name = "탈퇴", value = "탈퇴하여 더 이상 문제들을 받지 않습니다.", inline = False)
    embed.add_field(name = "알림", value = "알림에 관한 도움말을 봅니다.", inline = False)
    await ctx.send(embed = embed)

@bot.command(name = "가입")
async def 가입(ctx, *arg):
    if not arg: 
        embed = discord.Embed(title = f"가입 커맨드 사용법", description = "ㄱ가입 <solved.ac 핸들링>", color = GOLD_COLOR)
        await ctx.send(embed = embed)
        return
    if not getUser(ctx.author.id):
        embed = discord.Embed(
            title = f"🔔 가입 🔔",
            description = "가입해서 매일 나오는 무작위 문제들을 풀어보세요!",
            color = GOLD_COLOR
        )
        await ctx.send(embed = embed, view = RegisterUser(ctx, arg))
    else:
        embed = discord.Embed(
            title = "⚠️ 가입 실패 ⚠️",
            description='이미 가입되어 있는 유저입니다!',
            color = 0xed2b2a
        )
        await ctx.send(embed = embed)

@bot.command(name = "탈퇴")
async def 탈퇴(ctx, *arg):
    if getUser(ctx.author.id):
        embed = discord.Embed(
            title = f"🔔 탈퇴 🔔",
            description = "탈퇴해서 문제를 더 이상 받지 않습니다.",
            color = GOLD_COLOR
        )
        await ctx.send(embed = embed, view = DeleteUser(ctx, arg))
    else:
        embed = discord.Embed(
            title = "⚠️ 탈퇴 실패 ⚠️",
            description='가입되어 있지 않습니다.',
            color = discord.Color.red()
        )
        await ctx.send(embed = embed)

@bot.command(name = "알림")
async def 알림(ctx, *arg):
    if not arg: 
        embed = discord.Embed(title = f"알림 커맨드 사용법", description = "ㄱ알림 채널 <채널>\nㄱ알림 끄기\nㄱ알림 켜기", color = GOLD_COLOR)
        await ctx.send(embed = embed)
        return
    if arg[0] == "채널" and len(arg) == 1:
        embed = discord.Embed(title = f"알림 채널 커맨드 사용법", description = "ㄱ알림 채널 <채널>", color = GOLD_COLOR)
        await ctx.send(embed = embed)
        return
    if arg[0] in ["끄기", "켜기"]:
        if getGuild(ctx.guild.id) is None:
            for channel in ctx.guild.channels:
                if channel.type == discord.ChannelType.text:
                    addGuild(ctx.guild.id, channel.id)
                    break
        if arg[0] == "켜기":
            turnOnGuildNotion(ctx.guild.id)
        else:
            turnOffGuildNotion(ctx.guild.id)
        if arg[0] == "켜기":
            embed = discord.Embed(title = f"이 서버에서 봇의 알림을 켰습니다!", description = "이제 이 서버에 알림을 보내드립니다!", color = GOLD_COLOR)
        else:
            embed = discord.Embed(title = f"이 서버에서 봇의 알림을 껐습니다!", description = "더 이상 이 서버에는 알림을 보내지 않습니다!", color = GOLD_COLOR)
        await ctx.send(embed = embed)
        return
    if arg[0] == "채널":
        if getGuild(ctx.guild.id) is None:
            for channel in ctx.guild.channels:
                if channel.type == discord.ChannelType.text:
                    addGuild(ctx.guild.id, channel.id)
                    break
        if len(arg[1]) < 4:
            embed = discord.Embed(title = f"⚠️ 유효하지 않은 채널입니다. ⚠️", description = "확인 부탁드립니다.", color = discord.Color.red())
            await ctx.send(embed = embed)
            return
        try:
            channelId = int(arg[1][2:-1])
        except:
            embed = discord.Embed(title = f"⚠️ 유효하지 않은 채널입니다. ⚠️", description = "확인 부탁드립니다.", color = discord.Color.red())
            await ctx.send(embed = embed)
            return
        for channel in ctx.guild.channels:
            if channel.id == channelId:
                changeGuildNotionChannel(ctx.guild.id, channelId)
                embed = discord.Embed(title = f"알림 채널을 변경하였습니다!", description = f"{arg[1]} 에 알림을 보냅니다!", color = GOLD_COLOR)
                break
        else:
            embed = discord.Embed(title = f"⚠️ 해당 채널은 존재하지 않습니다. ⚠️", description = "확인 부탁드립니다.", color = discord.Color.red())
        await ctx.send(embed = embed)

@tasks.loop(seconds = 1)
async def alertEveryday():
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute
    second = now.second
    tester = second % 10 == -1
    if tester or second + minute + hour == 0:
        problemId, tier = getRandomProblem()
        await alertToGuilds(problemId, tier)

bot.run(TOKEN)