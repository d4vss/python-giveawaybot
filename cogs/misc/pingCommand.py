import disnake, os
from disnake import Embed
from disnake.ext import commands

class Ping(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(description="Zeigt dir die Latenz vom Bot.")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def ping(self, inter):
        embed = Embed(description=f"Discord websocket: **{round(self.client.latency * 1000)}ms**", color=0xffffff)
        await inter.send(embed=embed)

def setup(client):
    client.add_cog(Ping(client))