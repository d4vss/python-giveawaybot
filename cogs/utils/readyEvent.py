import disnake, sqlite3, os
from disnake.ext import commands
from datetime import datetime

class Ready(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        if not os.path.exists("assets"):
            os.makedirs("assets")
        conn = sqlite3.connect("assets/data.db")
        print('''{}
Disnake version: {}
Connected to Discord Gateway on {}.
{}'''.format("="*10, disnake.__version__, datetime.now().strftime("%d.%m.%Y at %H:%M"), "="*10))

def setup(client):
    client.add_cog(Ready(client))