import disnake
from disnake.ext import commands

class CommandLogger(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_application_command(self, inter):
        print("Slash command \"{}\" was executed by {} in {}.".format(inter.data.name, inter.author, inter.guild.name))

def setup(client):
    client.add_cog(CommandLogger(client))