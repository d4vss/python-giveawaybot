import os, disnake, dotenv, glob
from disnake.ext import commands

client = commands.InteractionBot(intents=disnake.Intents.all())
token = dotenv.get_key('.env', 'TOKEN')

print("{}".format("="*10))
for filename in glob.glob("cogs/**/*.py", recursive=True):
    n = filename.replace('\\', '.').replace('/', '.')
    if n.split('.')[2][0] == "~":
        print("Skipping {}.py".format(n.split('.')[2][1:]))
    else:
        client.load_extension(n.replace('.py', ''))
        print("Loaded {}.py".format(n.split('.')[2]))

client.run(token)