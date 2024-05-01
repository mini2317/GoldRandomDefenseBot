from discord.ext import tasks, commands
from discord.ui import View
import discord, datetime
from problemData import *
from guildData import *
from userData import *

bot = commands.Bot(command_prefix='ㄱ', intents = discord.Intents.all())
bot.remove_command('help')

def sortRank(userInfos, userId, option : UserDataIdx, count = 5) -> str:
    units = {
        UserDataIdx.streak : "일",
        UserDataIdx.longestStreak : "일",
        UserDataIdx.gold : "골드",
        UserDataIdx.solvedCnt : "개"
    }
    count = min(count, len(userInfos))
    s = sorted(userInfos, key = lambda x: x[option], reverse = True)
    idOfUsers = tuple(map(lambda x : x[UserDataIdx.userId], s))
    tmp = '\n'.join(f'**{i + 1}위**. {bot.get_user(idOfUsers[i]).name} ({s[i][UserDataIdx.handle]}) - {s[i][option]} {units[option]}' for i in range(count))
    if userId in idOfUsers[:count]:
        idx = idOfUsers.index(userId)
        tmp += f'\n\n**{idx + 1}위** (상위 {"%.2f" % ((idx + 1) / len(idOfUsers) * 100)}%). {bot.get_user(userId).name} ({s[idx][UserDataIdx.handle]}) - {s[idx][option]} {units[option]}'
    return tmp

def displayRank(ctx, arg, embed, userInfos):
    if not arg:
        embed.add_field(name = "🔥 현재 스트릭 🔥", value = sortRank(userInfos, ctx.author.id, UserDataIdx.streak), inline = False)
        embed.add_field(name = "✨ 최장 스트릭 ✨", value = sortRank(userInfos, ctx.author.id, UserDataIdx.longestStreak), inline = False)
        embed.add_field(name = "🪙 골드 🪙", value = sortRank(userInfos, ctx.author.id, UserDataIdx.gold), inline = False)
        embed.add_field(name = "🔑 현재 까지 푼 랜덤 골드 문제 수 🔑", value = sortRank(userInfos, ctx.author.id, UserDataIdx.solvedCnt), inline = False)
    else:
        if arg[0] in ["스트릭", "현재", "ㅎㅈ", "ㅅㅌㄹ", "스", "ㅅ", "현"]:
            embed.add_field(name = "🔥 현재 스트릭 🔥", value = sortRank(userInfos, ctx.author.id, UserDataIdx.streak, count = 10), inline = False)
        elif arg[0] in ["최장", "ㅊㅈ", "ㅊ", "최", "장", "ㅈ"]:
            embed.add_field(name = "✨ 최장 스트릭 ✨", value = sortRank(userInfos, ctx.author.id, UserDataIdx.longestStreak, count = 10), inline = False)
        elif arg[0] in ["골드", "돈", "ㄷ", "ㄱㄷ", "ㄱ", "골"]:
            embed.add_field(name = "🪙 골드 🪙", value = sortRank(userInfos, ctx.author.id, UserDataIdx.gold, count = 10), inline = False)
        elif arg[0] in ["수", "문제", "ㅅ", "ㅁㅈ", "문"]:
            embed.add_field(name = "🔑 현재 까지 푼 랜덤 골드 문제 수 🔑", value = sortRank(userInfos, ctx.author.id, UserDataIdx.solvedCnt, count = 10), inline = False)
        else:
            embed.add_field(name = "🔥 현재 스트릭 🔥", value = sortRank(userInfos, ctx.author.id, UserDataIdx.streak), inline = False)
            embed.add_field(name = "✨ 최장 스트릭 ✨", value = sortRank(userInfos, ctx.author.id, UserDataIdx.longestStreak), inline = False)
            embed.add_field(name = "🪙 골드 🪙", value = sortRank(userInfos, ctx.author.id, UserDataIdx.gold), inline = False)
            embed.add_field(name = "🔑 현재 까지 푼 랜덤 골드 문제 수 🔑", value = sortRank(userInfos, ctx.author.id, UserDataIdx.solvedCnt), inline = False)

def getTargetUser(ctx, arg):
    target = ctx.author
    if arg:
        query = ' '.join(arg)
        for member in UserData.getEveryUsers():
            member = bot.get_user(member[UserDataIdx.userId])
            if member.id == query:
                target = member
                break
            if member.mention == query:
                target = member
                break
            if member.name == query:
                target = member
                break
            if str(member.id) == query:
                target = member
                break
        else:
            for member in ctx.author.guild.members:
                if not UserData.get(member.id):
                    continue
                if member.nick == query:
                    target = member
                    break
    return target

def addGuildWithDefaultChannel(guild):
    if not GuildData.get(guild.id):
        for channel in guild.channels:
            if channel.type == discord.ChannelType.text:
                GuildData.add(guild.id, channel.id)
                break
        else:
            GuildData.add(guild.id, -1)

async def setProblemOfTodayAndAlert(problem : Problem):
    setJson(PROBLEM_OF_TODAY_JSON_PATH, problem.info)
    for guild in bot.guilds:
        addGuildWithDefaultChannel(guild)
        if GuildData.get(guild.id)[0][2]:
            nowGuild = GuildData.get(guild.id)[0]
            if nowGuild[1] == -1:
                for channel in guild.channels:
                    if channel.type == discord.ChannelType.text:
                        GuildData.changeNotionChannel(guild.id, channel.id)
                        break
                else:
                    return
            testChannel = bot.get_guild(guild.id).get_channel(nowGuild[1])
            embed = discord.Embed(title = "오늘의 골드 문제입니다!", description = f"[{problem.problemId} - {problem('titleKo')}](https://www.acmicpc.net/problem/{problem.problemId})", color = GOLD_COLOR)
            embed.set_thumbnail(url = GOLD_IMAGE[15 - problem("level")])
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
        if UserData.get(user.id):
            embed = discord.Embed(
                title = "⚠️ 가입 실패 ⚠️",
                description='이미 가입되어 있는 유저입니다!',
                color = discord.Color.red()
            )
            await self.ctx.send(embed = embed)
            return
        if self.disabled or (not interaction.user.id == user.id):
            return
        self.disabled = True
        UserData.add(user.id, self.arg[0])
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
        if not UserData.get(user.id):
            embed = discord.Embed(
                title = "⚠️ 탈퇴 실패 ⚠️",
                description='가입되어 있지 않습니다.',
                color = discord.Color.red()
            )
            await self.ctx.send(embed = embed)
            return
        if self.disabled or (not interaction.user.id == user.id):
            return
        self.disabled = True
        UserData.delete(user.id)
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

@bot.command(name = "개발자")
async def 개발자(ctx, *arg):
    if not len(arg):
        await ctx.send(f'``ㄱ개발자 도움``')
        return
    if arg[0] != "도움":
        await ctx.send(f'``ㄱ개발자 도움``')
        return
    embed = discord.Embed(title = f"개발자 도움 <:goldQuestion:1234746108362756137>", color = GOLD_COLOR)
    embed.add_field(name = "핑", value = "핑을 보냄", inline = False)
    embed.add_field(name = "문제제거 <문제 번호>", value = "해당 문제를 데이터베이스에서 제거", inline = False)
    embed.add_field(name = "스트릭 증가 [타겟]", value = "사용자의 스트릭을 1 증가시킵니다.", inline = False)
    embed.add_field(name = "스트릭 리셋 [타겟]", value = "사용자의 스트릭을 0으로 설정합니다.", inline = False)
    embed.add_field(name = "스트릭 하루", value = "하루 후의 스트릭 연산을 모든 유저에게 시전합니다. **(+백업)**", inline = False)
    embed.add_field(name = "골드증가 <숫자> [타겟]", value = "사용자의 골드가 <숫자>만큼 증가합니다.", inline = False)
    embed.add_field(name = "리워드 [타겟]", value = "사용자의 골드가 리워드만큼 증가합니다.", inline = False)
    embed.add_field(name = "뽑기", value = "무작위 골드 문제를 내서 모든 서버에 알림을 보냄", inline = False)
    embed.add_field(name = "문제 재구성", value = "문제 테이블을 drop한 후 다시 문제를 채워넣습니다. **(+백업)**", inline = False)
    embed.add_field(name = "전체 재구성", value = "모든 테이블을 drop한 후 다시 구성합니다. 다시 문제도 다시 채워넣습니다. **(+백업)**", inline = False)
    embed.add_field(name = "리필", value = "문제 json파일을 로컬 테이블로부터 정보를 가져와 채워넣습니다.", inline = False)
    embed.add_field(name = "백업", value = "백업 파일을 생성합니다.", inline = False)
    await ctx.send(embed = embed)

@bot.command()
async def 핑(ctx):
    if ctx.author.id in BOT_ADMINS_ID:
        await ctx.send(f'``{bot.latency * 1000}ms``')
    
@bot.command()
async def 백업(ctx):
    if ctx.author.id in BOT_ADMINS_ID:
        await ctx.send(f'``백업을 시작합니다.``')
        backupDatabase()
        await ctx.send(f'``백업 완료.``')

@bot.command()
async def 스트릭(ctx, *arg):
    if ctx.author.id in BOT_ADMINS_ID and arg:
        if arg[0] == "증가":
            await ctx.send(f'``스트릭을 증가시킵니다.``')
            UserData.updateStreak(getTargetUser(ctx, arg[1:]).id)
            await ctx.send(f'``스트릭 증가 성공``')
        elif arg[0] == "리셋":
            await ctx.send(f'``스트릭을 리셋시킵니다.``')
            UserData.resetStreak(getTargetUser(ctx, arg[1:]).id)
            await ctx.send(f'``스트릭 리셋 성공``')
        elif arg[0] == "하루":
            await ctx.send(f'``이 상태로 하루가 끝났을 때의 연산 시행``')
            backupDatabase()
            UserData.updateUsersStreak(getFromJson(PROBLEM_OF_TODAY_JSON_PATH)["problemId"])
            await ctx.send(f'``스트릭 연산 성공``')

@bot.command()
async def 골드증가(ctx, *arg):
    if not len(arg):
        await ctx.send(f'``골드증가 <숫자>``')
        return
    if ctx.author.id in BOT_ADMINS_ID:
        await ctx.send(f'``골드를 증가시킵니다.``')
        UserData.addGold(getTargetUser(ctx, arg[1:]).id, int(arg[0]))
        await ctx.send(f'``골드 증가 성공``')

@bot.command()
async def 리워드(ctx, *arg):
    if ctx.author.id in BOT_ADMINS_ID:
        await ctx.send(f'``리워드를 받습니다.``')
        reward = UserData.addRewardGold(getTargetUser(ctx, arg[1:]).id)
        await ctx.send(f'``{reward} 골드 휙득``')

@bot.command()
async def 문제제거(ctx, *arg):
    if not len(arg): 
        await ctx.send(f'``문제제거 <문제번호>``')
        return
    if ctx.author.id in BOT_ADMINS_ID:
        await ctx.send(f'``{arg[0]}제거 시도``')
        ProblemData.deleteById(int(arg[0]))
        await ctx.send(f'``{arg[0]}제거 완료``')

@bot.command()
async def 뽑기(ctx):
    if ctx.author.id in BOT_ADMINS_ID:
        problem = ProblemData.popRandomProblem()
        await setProblemOfTodayAndAlert(problem)

@bot.command()
async def 문제(ctx, *arg):
    if ctx.author.id in BOT_ADMINS_ID:
        if not len(arg): return
        if arg[0] != "재구성": return
        backupDatabase()
        await ctx.send(f'``문제 테이블 제거 후 api에서 다시 정보를 가져오는 중..``')
        ProblemData.remakeDatabaseTable()
        await ctx.send(f'``문제 테이블이 성공적으로 재구성되었습니다!``')

@bot.command()
async def 전체(ctx, *arg):
    if ctx.author.id in BOT_ADMINS_ID:
        if not len(arg): return
        if arg[0] != "재구성": return
        backupDatabase()
        await ctx.send(f'``데이터베이스 초기화 시작``')
        dropEveryDataBases()
        await ctx.send(f'``테이블 구조 재구성 중...``')
        initializeDataBase()
        await ctx.send(f'``문제를 가져오는 중...``')
        ProblemData.remakeDatabaseTable()
        await ctx.send(f'``데이터베이스 테이블이 성공적으로 재구성되었습니다!``')

@bot.command()
async def 리필(ctx):
    if ctx.author.id in BOT_ADMINS_ID:
        ProblemData.refillJson()
        await ctx.send(f'``json이 초기화 된 후 다시 업데이트되었습니다!``')

@bot.command(name = "도움")
async def 도움(ctx, *arg):
    embed = discord.Embed(title = f"도움 <:goldQuestion:1234746108362756137>", color = GOLD_COLOR)
    embed.add_field(name = "소개", value = "이 봇에 대한 기본적인 정보들을 알아보세요!", inline = False)
    embed.add_field(name = "가입", value = "가입해서 매일 나오는 문제들을 풀어보세요!", inline = False)
    embed.add_field(name = "탈퇴", value = "탈퇴하여 기능의 일부를 이용하지 않습니다.", inline = False)
    embed.add_field(name = "정보", value = "사용자의 정보를 봅니다.", inline = False)
    embed.add_field(name = "랭킹", value = "전체 사용자들의 랭킹을 봅니다.", inline = False)
    embed.add_field(name = "서버랭킹", value = "서버 사용자들의 랭킹을 봅니다.", inline = False)
    embed.add_field(name = "오늘 문제", value = "오늘의 골드 문제를 봅니다.", inline = False)
    embed.add_field(name = "알림", value = "알림에 관한 도움말을 봅니다.", inline = False)
    embed.add_field(name = "초대링크", value = "봇의 초대링크를 받습니다.", inline = False)
    await ctx.send(embed = embed)

@bot.command(name = "소개")
async def 도움(ctx, *arg):
    embed = discord.Embed(title = f"소개글 <:goldQuestion:1234746108362756137>", color = GOLD_COLOR)
    embed.add_field(name = "개요", value = "이 봇은 비공식적으로 제작된 골드 랜덤 디펜스 봇입니다.\n이 봇은 원작자의 요청에 따라 언제든 서비스가 중단될 수 있습니다.", inline = False)
    embed.add_field(name = "서비스 내용", value = "매일 0시에 무작위 골드 문제를 받아보세요!\n가입까지 하신다면 골드 문제 스트릭 체킹 기능과 문제를 풀 때마다 봇 내에서의 재화인 **골드**를 얻으실 수 있습니다!", inline = False)
    embed.add_field(name = "제작자", value = "[@moomin_dev](https://github.com/mini2317)", inline = False)
    await ctx.send(embed = embed)

@bot.command(name = "초대링크")
async def 초대링크(ctx, *arg):
    embed = discord.Embed(title = f"초대링크 <:goldQuestion:1234746108362756137>", color = GOLD_COLOR)
    embed.add_field(name = "감사의 말", value = "이용해주셔서 감사드립니다! <:fhbt:1159345785528385606>", inline = False)
    embed.add_field(name = "초대링크", value = "[초대링크](https://discord.com/oauth2/authorize?client_id=1217056704101875722&permissions=3072&scope=bot)", inline = False)
    await ctx.send(embed = embed)

@bot.command(name = "문의")
async def 문의(ctx, *arg):
    text = ' '.join(arg)
    embed = discord.Embed(title = f"문의", color = GOLD_COLOR)
    embed.add_field(name = "문의내용", value = f"```{text}```", inline = False)
    await ctx.send(embed = embed)
    embed.add_field(name = "문의자 정보", value = f"```{ctx.author.name} ({ctx.author.id})```", inline = False)
    await bot.get_guild(INQUIRY_SERVER).get_channel(INQUIRY_CHANNEL).send(embed = embed)
    adminMention = ""
    for adminId in BOT_ADMINS_ID:
        adminMention += f'{bot.get_user(adminId).mention} '
    await bot.get_guild(INQUIRY_SERVER).get_channel(INQUIRY_CHANNEL).send(adminMention)

@bot.command(name = "가입")
async def 가입(ctx, *arg):
    if not arg: 
        embed = discord.Embed(title = f"가입 커맨드 사용법", description = "ㄱ가입 <solved.ac 핸들>", color = GOLD_COLOR)
        await ctx.send(embed = embed)
        return
    if not UserData.get(ctx.author.id):
        if not IsExistHandle(arg[0]):
            embed = discord.Embed(
                title = "⚠️ 가입 실패 ⚠️",
                description='존재하지 않는 핸들입니다!',
                color = discord.Color.red()
            )
            await ctx.send(embed = embed)
            return
        embed = discord.Embed(
            title = f"🔔 가입 🔔",
            description = "가입하시면 스트릭 체크, 골드 저장 등의 기능을 이용하실 수 있습니다.\n본인 핸들이라는 것에 대해 별다른 인증은 필요 없으나, 공부를 위한 봇이니 본인 핸들을 이용해주시길 바랍니다.",
            color = GOLD_COLOR
        )
        await ctx.send(embed = embed, view = RegisterUser(ctx, arg))
    else:
        embed = discord.Embed(
            title = "⚠️ 가입 실패 ⚠️",
            description='이미 가입되어 있는 유저입니다!',
            color = discord.Color.red()
        )
        await ctx.send(embed = embed)

@bot.command(name = "탈퇴")
async def 탈퇴(ctx, *arg):
    if UserData.get(ctx.author.id):
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

@bot.command(name = "정보")
async def 정보(ctx, *arg):
    target = getTargetUser(ctx, arg)
    if UserData.get(target.id):
        embed = discord.Embed(
            title = f"📒 {target.name} ({UserData.get(target.id)[UserDataIdx.handle]}) 님의 정보 📒",
            color = GOLD_COLOR
        )
        embed.add_field(name = "🔥 현재 스트릭 🔥", value = f"{UserData.get(target.id)[UserDataIdx.streak]} 일", inline = False)
        embed.add_field(name = "✨ 최장 스트릭 ✨", value = f"{UserData.get(target.id)[UserDataIdx.longestStreak]} 일", inline = False)
        embed.add_field(name = "🪙 골드 🪙", value = f"{UserData.get(target.id)[UserDataIdx.gold]} 골드", inline = False)
        embed.add_field(name = "🔑 현재 까지 푼 랜덤 골드 문제 수 🔑", value = f"{UserData.get(target.id)[UserDataIdx.solvedCnt]} 개", inline = False)
        await ctx.send(embed = embed)
    else:
        embed = discord.Embed(
            title = "⚠️ 정보 조회 실패 ⚠️",
            description='가입되어 있지 않습니다.',
            color = discord.Color.red()
        )
        await ctx.send(embed = embed)

@bot.command(name = "랭킹")
async def 랭킹(ctx, *arg):
    embed = discord.Embed(
        title = f"🌐 전체 이용자 랭킹 🌐",
        color = GOLD_COLOR
    )
    userInfos = UserData.getEveryUsers()
    displayRank(ctx, arg, embed, userInfos)
    await ctx.send(embed = embed)

@bot.command(name = "서버랭킹")
async def 서버랭킹(ctx, *arg):
    embed = discord.Embed(
        title = f"🏆 {ctx.guild.name} 서버의 랭킹 🏆",
        color = GOLD_COLOR
    )
    memebersId = tuple(map(lambda x: x.id, ctx.guild.members))
    userInfos = [user for user in UserData.getEveryUsers() if user[UserDataIdx.userId] in memebersId]
    displayRank(ctx, arg, embed, userInfos)
    await ctx.send(embed = embed)

@bot.command()
async def 오늘(ctx, *arg):
    if not arg:
        embed = discord.Embed(title = f"오늘 문제 커맨드 사용법", description = "ㄱ오늘 문제", color = GOLD_COLOR)
        await ctx.send(embed = embed)
        return
    if arg[0] != "문제":
        embed = discord.Embed(title = f"오늘 문제 커맨드 사용법", description = "ㄱ오늘 문제", color = GOLD_COLOR)
        await ctx.send(embed = embed)
        return
    problem = getFromJson(PROBLEM_OF_TODAY_JSON_PATH)
    embed = discord.Embed(title = "오늘의 골드 문제입니다!", description = f"[{problem['problemId']} - {problem['titleKo']}](https://www.acmicpc.net/problem/{problem['problemId']})", color = GOLD_COLOR)
    embed.set_thumbnail(url = GOLD_IMAGE[15 - problem["level"]])
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
        addGuildWithDefaultChannel(ctx.guild)
        if arg[0] == "켜기":
            GuildData.turnOnNotion(ctx.guild.id)
        else:
            GuildData.turnOffNotion(ctx.guild.id)
        if arg[0] == "켜기":
            embed = discord.Embed(title = f"이 서버에서 봇의 알림을 켰습니다!", description = "이제 이 서버에 알림을 보내드립니다!", color = GOLD_COLOR)
        else:
            embed = discord.Embed(title = f"이 서버에서 봇의 알림을 껐습니다!", description = "더 이상 이 서버에는 알림을 보내지 않습니다!", color = GOLD_COLOR)
        await ctx.send(embed = embed)
        return
    
    if arg[0] == "채널":
        addGuildWithDefaultChannel(ctx.guild)
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
                GuildData.changeNotionChannel(ctx.guild.id, channelId)
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
        UserData.updateUsersStreak(getFromJson(PROBLEM_OF_TODAY_JSON_PATH)["problemId"])
        problemId = ProblemData.popRandomProblem()
        await setProblemOfTodayAndAlert(problemId)

bot.run(TOKEN)