import disnake
from disnake import Embed
from disnake.ext import commands

class CommandError(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        if isinstance(error, commands.NotOwner) or isinstance(error, commands.MissingPermissions):
            embed = Embed(description="**You are missing permissions to execute this command!**", color=0xff0000)
            try:
                await inter.send(embed=embed, ephemeral=True)
            except:
                pass
        else:
            embed = Embed(description="**An unknown error occurred.**", color=0xff0000)
            try:
                await inter.send(embed=embed, ephemeral=True)
            except:
                pass
            raise error

def setup(client):
    client.add_cog(CommandError(client))