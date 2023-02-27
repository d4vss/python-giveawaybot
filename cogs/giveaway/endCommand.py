import disnake, time, aiosqlite, datetime as dt
from disnake import ButtonStyle
from disnake.ext import commands
from disnake.ext.commands import has_permissions
from humanize.time import precisedelta
from disnake.ui import Button

class EndCommand(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.slash_command(description="Show active giveaways.")
    @has_permissions(administrator=True)
    async def gend(self, inter, message_id):
        await inter.response.defer(ephemeral=True)
        if not message_id.isnumeric():
            return await inter.send("💥 That is not a valid message ID!", ephemeral=True)
        message_id = int(message_id)
        async with aiosqlite.connect("assets/data.db") as db:
            cursor = await db.execute("SELECT message_id, channel_id, guild_id, end_timestamp FROM giveaways WHERE message_id = ?", (message_id,))
            giveaway = await cursor.fetchone()
            if not giveaway:
                return await inter.send("💥 That is not a valid giveaway message ID!", ephemeral=True)
            message_id = giveaway[0]; channel_id = giveaway[1]; guild_id = giveaway[2]
            giveaway_message = await self.client.get_channel(channel_id).fetch_message(message_id)
            await db.execute("CREATE TABLE IF NOT EXISTS giveaway_entries (message_id INT, user_id INT)")
            cursor = await db.execute("SELECT * FROM giveaway_entries WHERE message_id = ?", (giveaway_message.id,))
            entries = len(await cursor.fetchall())

            winners_line = None
            for line in giveaway_message.embeds[0].description.splitlines():
                if line.startswith("Winners: "):
                    winners_line = line
                    break
            
            if entries == 0:
                await db.execute("DELETE FROM giveaways WHERE message_id = ?", (giveaway_message.id,))
                await db.commit()
                embed = giveaway_message.embeds[0]
                embed.description = giveaway_message.embeds[0].description.replace(winners_line, f"Winners:")
                embed.color = 0x282b30
                giveaway_summary = Button(style=ButtonStyle.url, label="Giveaway Summary", url="https://example.com/", disabled=True)
                await giveaway_message.edit(embed=embed, components=[giveaway_summary])
                await giveaway_message.reply("No valid entrants, so a winner could not be determined!", mention_author=False)
                return await inter.send(":tada: Successfully ended giveaway {}!".format(giveaway_message.id), ephemeral=True)

            winners_amount = int(winners_line.split(" ")[1].replace("**", ""))
            if entries <= winners_amount:
                winners_amount = entries

            cursor = await db.execute("SELECT * FROM giveaways WHERE message_id = ?", (giveaway_message.id,))
            if not await cursor.fetchone():
                return

            if entries >= winners_amount:
                cursor = await db.execute("SELECT * FROM giveaway_entries WHERE message_id = ? ORDER BY RANDOM() LIMIT ?", (giveaway_message.id, winners_amount))
                winners = await cursor.fetchall()

                winners_list = []
                for winner in winners:
                    winners_list.append(f"<@{winner[1]}>")
                
                embed = giveaway_message.embeds[0]
                embed.description = giveaway_message.embeds[0].description.replace(winners_line, f"Winners: **{'**, **'.join(winners_list)}**")
                embed.color = 0x282b30
                giveaway_summary = Button(style=ButtonStyle.url, label="Giveaway Summary", url="https://example.com/", disabled=True)
                await giveaway_message.edit(embed=embed, components=[giveaway_summary])

                await giveaway_message.reply("Congratulations {}! You won the **{}**!".format(", ".join(winners_list), embed.title), mention_author=False)
                await inter.send(":tada: Successfully ended giveaway {}!".format(giveaway_message.id), ephemeral=True)

                await db.execute("DELETE FROM giveaways WHERE message_id = ?", (giveaway_message.id,))
                await db.commit()

def setup(client):
    client.add_cog(EndCommand(client))