import os
import re
from dotenv import load_dotenv
import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
load_dotenv()

client = commands.Bot(command_prefix='.myu ', help_command=None)

cluster = MongoClient(os.getenv('DB_LINK'))
db = cluster["guilds"]
collection = db["test"]

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

@client.command(name='bonk')
async def bonk_member(ctx, arg):
    # member = await commands.MemberConverter().convert(ctx, arg)
    member = discord.utils.find(lambda m: re.search(arg, m.name, re.IGNORECASE), ctx.guild.members)
    print(member)
    await ctx.channel.send(member.mention + " U HAVE BEEN BONKED")

@client.command(name='reload')
async def reload_cog(ctx, file='cogs.GuildAdministration'):
    client.reload_extension(file)



client.load_extension('cogs.GuildAdministration')
client.run(os.getenv('BOT_TOKEN'))

