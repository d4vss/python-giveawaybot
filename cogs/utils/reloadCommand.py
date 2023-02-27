import disnake, os, glob
from disnake import Embed
from disnake.ext import commands
from datetime import datetime

class ReloadCommand(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(description="Reloads all cogs.")
    @commands.is_owner()
    async def reload(self, inter):
        done = 0
        total = 0

        embed = Embed(description="Reloading all cogs...", color=0xffffff)
        await inter.send(embed=embed, ephemeral=True)
        print("{}\n> Reloading all cogs.".format("="*10))

        for filename in glob.glob("cogs/**/*.py", recursive=True):
            n = filename.replace('\\', '.').replace('/', '.')
            if n.split('.')[2][0] != "~":
                try:
                    try: 
                        self.client.reload_extension(n.replace('.py', ''))
                        print("Reloaded {}.py".format(n.split('.')[2]))
                        done += 1
                    except:
                        self.client.load_extension(n.replace('.py', ''))
                        print("Loaded {}.py".format(n.split('.')[2]))
                        done += 1
                except:
                    print("Failed reloading {}.py".format(n.split('.')[2]))
                total += 1
                        
        print("> {} out of {} were reloaded at {}.\n{}".format(done, total, datetime.now().strftime("%d.%m.%y at %H:%M"), "="*10))
        embed = Embed(description="**{} out of {} were reloaded.**".format(done, total), color=0xffffff)   
        await inter.edit_original_message(embed=embed)

def setup(client):
    client.add_cog(ReloadCommand(client))