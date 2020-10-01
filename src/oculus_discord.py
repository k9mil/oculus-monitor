import discord
import oculus
from discord.ext import commands

client = commands.Bot(command_prefix = ".")

@client.command()
async def itemfound(ctx, *args):
    await ctx.send(f"Item has been found.")


client.run('...')