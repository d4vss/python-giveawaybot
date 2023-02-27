import disnake, os
from disnake import Embed
from disnake.ext import commands

class HelpCommand(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(description="Shows all commands.")
    async def help(self, inter):
        embed = Embed(title="Command list:", color=0xffffff)

        for command in self.client.slash_commands:
            if command.description:
                embed.add_field(name="/{}".format(command.name), value=command.description, inline=False)
            else:
                embed.add_field(name=command.name, value="No description.", inline=False)

        await inter.send(embed=embed, ephemeral=True)

def setup(client):
    client.add_cog(HelpCommand(client))