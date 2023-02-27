import disnake, time, aiosqlite
from disnake import TextInputStyle, ButtonStyle, Embed
from disnake.ui import TextInput, Modal, Button
from disnake.ext import commands
from disnake.ext.commands import has_permissions
from datetime import datetime

class CreateCommand(commands.Cog):
    def __init__(self, client):
        self.client = client

    # async def parseTimeLong(self, time_string):
    #     time_dict = {
    #         'second': 1,
    #         'minute': 60,
    #         'hour': 3600,
    #         'day': 86400,
    #         'week': 604800,
    #         'month': 2592000,
    #         'year': 31536000
    #     }
    #     if time_string[-1] == 's':
    #         time_string = time_string[:-1]
    #     value, unit = time_string.split()
    #     return int(value) * time_dict[unit]

    @commands.slash_command(description="Starts a giveaway (interactive).")
    @has_permissions(administrator=True)
    async def gcreate(self, inter):
        duration = TextInput(label="Duration", placeholder="Ex: 10 minutes", custom_id="gcreate_duration", min_length=2, max_length=4000)
        winners = TextInput(label="Number of winners", value="1", custom_id="gcreate_winners", min_length=1, max_length=2)
        prize = TextInput(label="Prize", custom_id="gcreate_prize")
        description = TextInput(label="Description", required=False, custom_id="gcreate_description", max_length=1000, style=TextInputStyle.long)

        modal = Modal(custom_id="gcreate_modal", title="Create a Giveaway", components=[duration, winners, prize, description])
        await inter.response.send_modal(modal=modal)

    @commands.Cog.listener()
    async def on_modal_submit(self, inter):
        if inter.custom_id == "gcreate_modal":
            duration = inter.text_values["gcreate_duration"]
            winners = inter.text_values["gcreate_winners"]
            prize = inter.text_values["gcreate_prize"]
            description = inter.text_values["gcreate_description"]

            seconds = await self.parseTimeLong(duration)
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

            embed = Embed(title=prize, timestamp=datetime.fromtimestamp(end_timestamp), color=0x5865F2)
            embed.description = ""
            if description:
                embed.description += "\n{}\n\n".format(description)    
            embed.description += "Ends: <t:{}:R> (<t:{}:F>)\nHosted by: {}\nEntries: **0**\nWinners: **{}**".format(end_timestamp, end_timestamp, inter.author.mention, winners)

            enter_giveaway = Button(style=ButtonStyle.blurple, emoji="🎉", custom_id="enter_giveaway")

            msg = await inter.channel.send(embed=embed, components=[enter_giveaway])
            async with aiosqlite.connect("assets/data.db") as db:
                await db.execute("CREATE TABLE IF NOT EXISTS giveaways (message_id INT, guild_id INT, channel_id INT, end_timestamp INT)")
                await db.execute("INSERT INTO giveaways (message_id, guild_id, channel_id, end_timestamp) VALUES (?, ?, ?, ?)", (msg.id, inter.guild.id, inter.channel.id, end_timestamp))
                await db.commit()

            await inter.send("The giveaway was successfully created! ID: {}".format(msg.id), ephemeral=True)

def setup(client):
    client.add_cog(CreateCommand(client))