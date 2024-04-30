from dataBasic import *
class GuildData:
    @staticmethod
    def get(guildId):
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

    @staticmethod
    def add(guildId, channelId):
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        cur.execute(f'''
            INSERT
            INTO "{GUILD_MASTER}" (guildId, channelId, canNotion)
            VALUES ("{guildId}", "{channelId}", 1)
        ''')
        con.commit()
        con.close()

    @staticmethod
    def changeNotionChannel(guildId, channelId):
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        cur.execute(f'''
            UPDATE "{GUILD_MASTER}"
            SET channelId = {channelId}
            WHERE guildId = '{guildId}'
        ''')
        con.commit()
        con.close()

    @staticmethod
    def turnOnNotion(guildId):
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        cur.execute(f'''
            UPDATE "{GUILD_MASTER}"
            SET canNotion = 1
            WHERE guildId = '{guildId}'
        ''')
        con.commit()
        con.close()

    @staticmethod
    def turnOffNotion(guildId):
        con = sqlite3.connect(DATABASE_PATH)
        cur = con.cursor()
        cur.execute(f'''
            UPDATE "{GUILD_MASTER}"
            SET canNotion = 0
            WHERE guildId = '{guildId}'
        ''')
        con.commit()
        con.close()