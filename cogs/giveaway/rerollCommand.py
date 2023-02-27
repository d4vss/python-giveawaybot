import disnake, time, aiosqlite, datetime as dt, random
from disnake.ext import commands
from disnake.ext.commands import has_permissions

class RerollCommand(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.slash_command(description="Rerolls one new winner from a giveaway.")
    @has_permissions(administrator=True)
    async def greroll(self, inter, message_id, count: int = 1):
        if count < 1:
            return await inter.send("💥 You must reroll at least one winner!", ephemeral=True)
        if not message_id.isdigit():
            return await inter.send("💥 The message ID must be a number!", ephemeral=True)
        async with aiosqlite.connect("assets/data.db") as db:
            cursor = await db.execute("SELECT * FROM giveaway_entries WHERE message_id = ?", (message_id,))
            users = await cursor.fetchall()

            tmp = await db.execute("SELECT * FROM giveaways WHERE message_id = ?", (message_id,))
            if await tmp.fetchone(): 
                return await inter.send("💥 This giveaway is still running!", ephemeral=True)
            
        if not users:
            return await inter.send("💥 No one took part in this giveaway or an error occurred on the bot side!", ephemeral=True)

        if count > len(users):
            count = len(users)
        
        winners = []
        for i in range(count):
            winner = random.choice(users)
            winners.append(winner)
            users.remove(winner)

        await inter.send(":tada: {} rerolled the giveaway! Congratulations {}!".format(inter.author.mention, ", ".join(["<@{}>".format(winner[1]) for winner in winners])))


def setup(client):
    client.add_cog(RerollCommand(client))