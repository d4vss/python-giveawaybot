import disnake, aiosqlite
from disnake import ButtonStyle
from disnake.ui import Button
from disnake.ext import commands
from disnake.ext.commands import has_permissions

class JoinLeaveEvent(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_button_click(self, inter):
        if inter.component.custom_id == "enter_giveaway":
            if inter.message.embeds:
                if inter.message.embeds[0].description:
                    if inter.message.embeds[0].description.startswith("Ends: ") or inter.message.embeds[0].description.contains("Ends: "):
                        async with aiosqlite.connect("assets/data.db") as db:
                            await db.execute("CREATE TABLE IF NOT EXISTS giveaway_entries (message_id INT, user_id INT)")
                            
                            cursor = await db.execute("SELECT * FROM giveaway_entries WHERE message_id = ? AND user_id = ?", (inter.message.id, inter.user.id))
                            if await cursor.fetchone():
                                leave_giveaway = Button(label="Leave giveaway", style=ButtonStyle.red, custom_id="leave_giveaway_{}".format(inter.message.id))
                                return await inter.send("You have already entered this giveaway!", ephemeral=True, components=[leave_giveaway])

                            await db.execute("INSERT INTO giveaway_entries VALUES (?, ?)", (inter.message.id, inter.user.id))
                            await db.commit()

                            cursor = await db.execute("SELECT * FROM giveaway_entries WHERE message_id = ?", (inter.message.id,))
                            entries = len(await cursor.fetchall())

                            for line in inter.message.embeds[0].description.splitlines():
                                if line.startswith("Entries: "):
                                    entries_line = line
                                    break
                            
                        embed = inter.message.embeds[0]
                        embed.description = inter.message.embeds[0].description.replace(entries_line, f"Entries: **{entries}**")
                        await inter.message.edit(embed=embed)

            await inter.response.defer()
        elif "leave_giveaway" in inter.component.custom_id:
            message_id = int(inter.component.custom_id.split("_")[2])
            async with aiosqlite.connect("assets/data.db") as db:
                await db.execute("CREATE TABLE IF NOT EXISTS giveaway_entries (message_id INT, user_id INT)")
                await db.commit()

                cursor = await db.execute("SELECT * FROM giveaway_entries WHERE message_id = ?", (message_id,))
                entries = len(await cursor.fetchall())
                
                entries_line = None
                giveaway_message = await inter.channel.fetch_message(message_id)
                for line in giveaway_message.embeds[0].description.splitlines():
                    if line.startswith("Entries: "):
                        entries_line = line
                        break

                if not entries_line:
                    return await inter.send("💥 You cannot enter or leave this giveaway because it has already ended!", ephemeral=True)

            embed = giveaway_message.embeds[0]
            embed.description = giveaway_message.embeds[0].description.replace(entries_line, f"Entries: **{entries}**")
            await giveaway_message.edit(embed=embed)

            await inter.response.edit_message(":tada: You have successfully left the giveaway!", components=None)

def setup(client):
    client.add_cog(JoinLeaveEvent(client))