import disnake, time, aiosqlite
from disnake import ButtonStyle
from disnake.ui import Button
from disnake.ext import commands, tasks

class EvalEvent(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.eval_giveaways.start()

    @tasks.loop(seconds=.5)
    async def eval_giveaways(self):
        async with aiosqlite.connect("assets/data.db") as db:
            await db.execute("CREATE TABLE IF NOT EXISTS giveaways (message_id INT, guild_id INT, channel_id INT, end_timestamp INT)")
            cursor = await db.execute("SELECT message_id, channel_id, guild_id, end_timestamp FROM giveaways")
            giveaways = await cursor.fetchall()
            for giveaway in giveaways:
                message_id = giveaway[0]; channel_id = giveaway[1]; guild_id = giveaway[2]
                try:
                    giveaway_message = await self.client.get_channel(channel_id).fetch_message(message_id)
                except:
                    await db.execute("DELETE FROM giveaways WHERE message_id = ?", (message_id,))
                    await db.execute("DELETE FROM giveaway_entries WHERE message_id = ?", (message_id,))
                    await db.commit()
                    continue
                
                if giveaway[3] > time.time():
                    continue

                if giveaway_message.embeds:
                    if giveaway_message.embeds[0].description:
                        if "Ends: " in giveaway_message.embeds[0].description:
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
                                return await giveaway_message.reply("No valid entrants, so a winner could not be determined!", mention_author=False)

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

                                await db.execute("DELETE FROM giveaways WHERE message_id = ?", (giveaway_message.id,))
                                await db.commit()

    @eval_giveaways.before_loop
    async def before_eval_giveaways(self):
        await self.client.wait_until_ready()

def setup(client):
    client.add_cog(EvalEvent(client))