from discord.ext import commands
import os
import traceback
import discord
import asyncio

bot = commands.Bot(command_prefix='/')
token = os.environ['DISCORD_BOT_TOKEN']


@bot.command(name="こんにちは")
async def hello(ctx):
    await ctx.send(f"どうも、{ctx.message.author.name}さん！")
    await ctx.send(f"どうも、{ctx.message.author}さん！")
    
@bot.event
async def on_command_error(ctx, error):
    await ctx.send(str(error))
    await ctx.send('Logged in as')
    await ctx.send(bot.user.name)
    await ctx.send(bot.user.id)
    await ctx.send('------')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')
    await ctx.send('goodbye')

@bot.command()
async def add(ctx, a: int, b: int):
    await ctx.send(a+b)

@bot.command()
async def multiply(ctx, a: int, b: int):
    await ctx.send(a*b)

@bot.command()
async def greet(ctx):
    await ctx.send(":smiley: :wave: Hello, there!")

bot.run(token)
