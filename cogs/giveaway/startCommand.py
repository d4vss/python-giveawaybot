import disnake, time, aiosqlite
from disnake import Embed, ButtonStyle
from disnake.ui import Button
from disnake.ext import commands
from disnake.ext.commands import has_permissions
from datetime import datetime

class StartCommand(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def parseTimeShort(self, time_string):
        time_dict = {
            "s": 1,
            "m": 60,
            "h": 3600,
            "d": 86400,
            "w": 604800,
            "o": 2592000,
            "y": 31536000
        }
        if time_string[-1] == 'o':
            return int(time_string[:-2]) * 2592000
        return int(time_string[:-1]) * time_dict[time_string[-1]]

    @commands.slash_command(description="Starts a giveaway.")
    @has_permissions(administrator=True)
    async def gstart(self, inter, duration, winners : int, prize):
        seconds = await self.parseTimeShort(duration)
        if not seconds:
            return await inter.send("I could not convert ``{}`` to a valid length of time!".format(duration), ephemeral=True)

        if seconds < 10:
            return await inter.send("The duration you provided ({}) was shorter than the minimum duration (**10** seconds)!".format(seconds), ephemeral=True)

        end_timestamp = round(time.time() + seconds)

        try:
            winners = int(winners)
            if winners < 1 or winners > 20:
                return await inter.send("The number of winners you provided ({}) was not between 1 and 20!".format(winners), ephemeral=True)
        except:
            return await inter.send("I could not convert ``{}`` to a valid number of winners!".format(winners), ephemeral=True)

        embed = Embed(title=prize, description="Ends: <t:{}:R> (<t:{}:F>)\nHosted by: {}\nEntries: **0**\nWinners: **{}**".format(end_timestamp, end_timestamp, inter.author.mention, winners), timestamp=datetime.fromtimestamp(end_timestamp), color=0x5865F2)
        enter_giveaway = Button(style=ButtonStyle.blurple, emoji="🎉", custom_id="enter_giveaway")

        msg = await inter.channel.send(embed=embed, components=[enter_giveaway])
        async with aiosqlite.connect("assets/data.db") as db:
            await db.execute("CREATE TABLE IF NOT EXISTS giveaways (message_id INT, guild_id INT, channel_id INT, end_timestamp INT)")
            await db.execute("INSERT INTO giveaways (message_id, guild_id, channel_id, end_timestamp) VALUES (?, ?, ?, ?)", (msg.id, inter.guild.id, inter.channel.id, end_timestamp))
            await db.commit()

        await inter.send("The giveaway was successfully created! ID: {}".format(msg.id), ephemeral=True)

def setup(client):
    client.add_cog(StartCommand(client))