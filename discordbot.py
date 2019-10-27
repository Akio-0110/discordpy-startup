# Work with Python 3.6.6
import random
#import asyncio
import discord
import mysql.connector
from mysql.connector import errorcode
#from discord import Game
#from discord.ext.commands import Bot

TOKEN = 'NjEyODEyMTk2NTAxNTIwMzg0.Xan1dw.SI6zzUOixE1WZcuQI2XK0jS1rQE'
client = discord.Client()

# MySQL接続
cnt = mysql.connector.connect(
    host='us-cdbr-iron-east-02.cleardb.net',
    port='3306',
    db='heroku_0b2656996c2477a',
    user='b600998caa803a',
    password='7d7aec23',
    charset='utf8'
)

# コネクションが切れた時に再接続してくれるよう設定
cnt.ping(reconnect=True)

# カーソル取得
db = cnt.cursor(buffered=True)

#################################
# Usage文
#################################
usage_avalon0 ="""
 現在使えるコマンド
   h/help   : ヘルプ（コマンド一覧）
   m/make   : 村作成
"""

usage_avalon1="""
 現在使えるコマンド
   h/help   : ヘルプ（コマンド一覧）
   in/login : 村入室
   s/start  : 開始
"""

usage_avalon2="""
 現在使えるコマンド
   h/help   : ヘルプ（コマンド一覧）
   s/stop   : ゲーム停止
"""

usage_avalon3="""
 現在使えるコマンド
   h/help   : ヘルプ（コマンド一覧）
   s/stop   : ゲーム停止
"""

@client.event
async def on_ready():
    sql = "update `avalon_data` set \
    `game_status`= 0, \
    `quest_cnt`= 0, \
    `game_phase`= 0, \
    `game_stop`= 0, \
    `game_member_num`= 0"
    db.execute(sql)
    # テーブル作成
    sql = "create table if not exists `avalon_user` ( \
    `id` int, \
    `name` varchar(255), \
    `user_id` bigint, \
    primary key (`id`) \
    )"
    db.execute(sql)
    # await ctx.channel.send(f"こんにちは")
    sql = 'SELECT * FROM `avalon_data`'
    db.execute(sql)
    rows = db.fetchall()
    for i in rows:
        print(f"{i[0]}, {i[1]}, {i[2]}, {i[3]}, {i[4]}, {i[5]}, {i[6]}")
    print("Logged in as " + client.user.name)

@client.event
async def on_message(ctx):
    sql = 'SELECT * FROM `avalon_data` where id = 0'
    db.execute(sql)
    rows = db.fetchall()
    for i in rows:
        game_status=i[1]
        quest_cnt=i[2]
        vote_cnt=i[3]
        game_phase=i[4]
        game_stop=i[5]
        game_member_num=i[6]

    print(f"game_status = {game_status}, quest_cnt = {quest_cnt}, vote_cnt = {vote_cnt}, game_phase = {game_phase}, game_stop = {game_stop}, game_member_num = {game_member_num}")

    # help : 村作成
    if ctx.content == 'h' or ctx.content == 'help':
        if game_status == 0:
            await ctx.channel.send(f"{usage_avalon0}")
        elif game_status == 1:
            await ctx.channel.send(f"{usage_avalon1}")
        elif game_status == 2:
            await ctx.channel.send(f"{usage_avalon2}")
        elif game_status == 3:
            await ctx.channel.send(f"{usage_avalon3}")
        #await ctx.channel.send(f"{ctx.author.id}")

    # make : 村作成
    elif ctx.content == 'm' or ctx.content == 'make':
        if game_status == 0:
            sql = f"insert into `avalon_user` (`id`, `name`, `user_id`) \
            values (%s, %s, %s)"
            val1 = "1"
            val2 = f"{ctx.author.name}"
            val3 = f"{ctx.author.id}"
            db.execute(sql, (val1,val2,val3))
            sql = f"update `avalon_data` set `game_status`=1 where id = 0"
            db.execute(sql)
            sql = f"update `avalon_data` set `game_member_num`=1 where id = 0"
            db.execute(sql)
            await ctx.channel.send(f"{ctx.author.name}が村を作成し、入室しました。 \
            \n現在１人です。\n５人以上集まればゲームを開始できます。")
        else :
            await ctx.channel.send(f"{ctx.content}コマンドは無効です。")

    # login : 村入室
    elif ctx.content == 'in' or ctx.content == 'login':
        if game_status == 1:
            # sql = 'SELECT game_member_num FROM `avalon_data` where id = 1'
            # db.execute(sql)
            # rows = db.fetchone()
            # gm_num = int(rows[0]) + 1
            gm_num = game_member_num + 1
            await ctx.channel.send(f"{gm_num}人目:{ctx.author.name}が村に入室しました。")
            sql = f"update `avalon_data` set `game_member_num` = {gm_num} where id = 0"
            db.execute(sql)
            sql = f"insert into `avalon_user` (`id`, `name`, `user_id`) \
            values (%s, %s, %s)"
            val1 = f"{gm_num}"
            val2 = f"{ctx.author.name}"
            val3 = f"{ctx.author.id}"

            db.execute(sql, (val1,val2,val3))
            sql = f"SELECT id FROM `avalon_user`"
            db.execute(sql)
            id = db.fetchone()
            sql = f"SELECT name FROM `avalon_user`"
            db.execute(sql)
            name = db.fetchone()
            sql = f"SELECT user_id FROM `avalon_user`"
            db.execute(sql)
            user_id = db.fetchone()
        else :
            await ctx.channel.send(f"{ctx.content}コマンドは無効です。")

    # start game : ゲームを開始する
    elif ctx.content == 's' or ctx.content == 'start' or ctx.content == 'stop':
        #await ctx.channel.send(f"game_status = {game_status}, command = {ctx.content}")
        if (game_status == 1) and (ctx.content == 's' or ctx.content == 'start'):
            if game_member_num > 4:
                #await ctx.channel.send(f"{ctx.content}コマンドは無効です。")
                # await ctx.author.send(f"{gm_num}人目:{name[0]}が村に入室しました。\
                # msg = client.get_user(user_id[0])
                # await ctx.author.send(f"{user_id[0]}")
                #await msg.send(f"ゲームを開始します。")
                await ctx.channel.send("ゲームを開始します。\n配役の公開機能を後で実装します。")
                sql = f"update `avalon_data` set `game_status`=2 where id = 0"
                db.execute(sql)
                quest_cnt = 1
                sql = f"update `avalon_data` set `quest_cnt`={quest_cnt} where id = 0"
                db.execute(sql)
                vote_cnt = 1
                sql = f"update `avalon_data` set `vote_cnt`={vote_cnt} where id = 0"
                db.execute(sql)
                game_phase = 1
                sql = f"update `avalon_data` set `game_phase`={game_phase} where id = 0"
                db.execute(sql)
            else :
                await ctx.channel.send(f"５人以上入室してからゲームを開始してください。\
                \n現在{game_member_num}人です。\
                \nあと{5-game_member_num}以上入室してからsコマンドを実行してください。")
        elif (game_status > 1) and (ctx.content == 's' or ctx.content == 'stop'):
            await ctx.channel.send("stopコマンドのため、ゲーム途中ですが、ゲームを停止します。")
            sql = "update `avalon_data` set \
            `game_status`= 0, \
            `quest_cnt`= 0, \
            `vote_cnt`= 0, \
            `game_phase`= 0, \
            `game_stop`= 0, \
            `game_member_num`= 0"
            db.execute(sql)
        else :
            await ctx.channel.send(f"{ctx.content}コマンドは無効です。")


    # connect check
    # elif ctx.content == 'c':


        # SQLクエリ実行（データ追加）
        #sql = 'INSERT INTO avalon_data(name) VALUES("nero claudius")';
        #db.execute(sql)

        # SQLクエリ実行（データ取得）
        # sql = 'SELECT game_status FROM avalon_data';
        # db.execute(sql)
        #
        # # 表示
        # rows = db.fetchall()
        # print(rows)
        #
        # # カーソル終了
        # db.close()
        # # MySQL切断
        # cnt.close()

#        await ctx.channel.send(ctx.author)
    # reset : 初期化
    elif ctx.content == 'r' or ctx.content == 'reset':
        sql = 'drop table avalon_data'
        db.execute(sql)
        sql = 'drop table avalon_user'
        db.execute(sql)
        await ctx.channel.send(f"データを初期化しました。")

    # カーソル終了
    #db.close()
    # MySQL切断
    #cnt.close()

client.run(TOKEN)
