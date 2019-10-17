from discord.ext import commands
import os
import discord
import asyncio
import MySQLdb

#int number

client = discord.Client()
token = os.environ['DISCORD_BOT_TOKEN']

#################################
# Usage文
#################################
Usage_avalon="""
 コマンド
   m   : 村作成
   v   : 承認
   q   : 却下
   s   : 成功
   f   : 失敗
"""

#@bot.command(name="こんにちは")
#async def hello(ctx):
#    await ctx.author.send(f"どうも、{ctx.message.author.name}さん！")
#    await ctx.author.send(f"どうも、{ctx.message.author}さん！")

#@bot.command(name="make")
#async def Make(ctx, arg):
#    await ctx.channel.send(f"{arg}を作成しました。")
    #con = MySQLdb.connect(
    #    user='b600998caa803a',
    #    passwd='7d7aec23',
    #    host='us-cdbr-iron-east-02.cleardb.net',
    #    db='heroku_0b2656996c2477a')
    #await ctx.channel.send(f"データベースにアクセスしました。")
    #cur = con.cursor()
    #cursor.execute('select * from avalon_data')
    #row = cursor.fetchone()

    #await ctx.channel.send(f"game_status = {row}")
    #await ctx.channel.send(f"quest_cnt = {row}")
    #await ctx.channel.send(f"vote_cnt = {row}")
    #await ctx.channel.send(f"game_phase = {row}")
    #await ctx.channel.send(f"game_stop = {row}")
    #game_status = 1
    #quest_cnt = 2
    #vote_cnt = 3
    #game_phase = 4
    #game_stop = 5
    #cursor.excute("insert into avalon_data
    #  (game_status, quest_cnt, vote_cnt, game_phase, game_stop)
    #    values (%d, %d, %d, %d, %d)",
    #        (game_status, quest_cnt, vote_cnt, game_phase, game_stop))
    #cursor.execute('select * from avalon_data')
    #row = cursor.fetchone()
    #await ctx.channel.send(f"game_status = {row}")
    #await ctx.channel.send(f"quest_cnt = {row}")
    #await ctx.channel.send(f"vote_cnt = {row}")
    #await ctx.channel.send(f"game_phase = {row}")
    #await ctx.channel.send(f"game_stop = {row}")

#@bot.command(name="f")
#async def Close(ctx):
    #cursor.close()
    #con.close()
    #await ctx.channel.send(f"データベースを初期化します")

#@bot.command(name="in")
#async def hello(ctx):
    #if (number is None) number = 0
    #await ctx.channel.send(f"{number}人目：{ctx.message.author.name}さんが入室しました")
#    await ctx.channel.send(f"人目：{ctx.message.author.name}さんが入室しました")

@client.event
async def on_command_error(ctx, error):
    await ctx.send(str(error))
    await ctx.send('Logged in as')
    await ctx.send(client.user.name)
    await ctx.send(client.user.id)
    await ctx.send('------')

@client.event
async def on_massage(message):
    #################################
    # ヘルプコマンド:?help
    #################################
    #if message.content.startswith("h"):
    #    if bot.user != message.author:
    #        m = Usage_avalon
    #        await bot.send_message(message.channel, m)
#            await client.send_message(message.channel, m)

#@bot.command()
#async def ping(ctx):
#    await ctx.send('pong')
#    await ctx.send('goodbye')

#@bot.command()
#async def add(ctx, a: int, b: int):
#    await ctx.send(a+b)

#@bot.command()
#async def multiply(ctx, a: int, b: int):
#    await ctx.send(a*b)

#@bot.command()
#async def greet(ctx):
#    await ctx.send(":smiley: :wave: Hello, there!")

bot.run(token)
