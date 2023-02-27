import disnake, time, aiosqlite, datetime as dt
from disnake.ext import commands
from disnake.ext.commands import has_permissions
from humanize.time import precisedelta

class ListCommand(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.slash_command(description="Show active giveaways.")
    @has_permissions(administrator=True)
    async def glist(self, inter):
        embed = disnake.Embed(title="Active Giveaways", color=0x5865F2)

        async with aiosqlite.connect("assets/data.db") as db:
            cursor = await db.execute("SELECT * FROM giveaways")
            rows = await cursor.fetchall()

        if len(rows) == 0:
            return await inter.send("💥 There are no giveaways currently running!", ephemeral=True)
            
        await inter.response.defer()
        for row in rows:
            giveaway_message = await inter.guild.get_channel(row[2]).fetch_message(row[0])
            delta = dt.timedelta(seconds=row[3] - time.time())
            ends_time = "Ends: " + precisedelta(delta, format="%0.0f")
            for line in giveaway_message.embeds[0].description.splitlines():
                if line.startswith("Hosted by:"):
                    hoster = line.split("Hosted by: ")[1]
                elif line.startswith("Winners:"):
                    winner_amount = line.split("Winners: **")[1].split("**")[0]
            embed.add_field(name=giveaway_message.embeds[0].title, value="[`{}`]({}) | {} | Winners: **{}** | Hosted by: {} | {}".format(giveaway_message.id, giveaway_message.jump_url, giveaway_message.channel.mention, winner_amount, hoster, ends_time))
        await inter.send(embed=embed)

def setup(client):
    client.add_cog(ListCommand(client))