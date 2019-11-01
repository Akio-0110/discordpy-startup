# Work with Python 3.6.6
import os
import random
import asyncio
import discord
import mysql.connector
from mysql.connector import errorcode
#from mysql.connector import pooling

#from discord import Game

TOKEN = os.environ['DISCORD_BOT_TOKEN']
client = discord.Client()

# MySQL接続
cnt = mysql.connector.connect(
    host=os.environ['DB_HOST'],
    port='3306',
    db=os.environ['DB_DATABASE'],
    user=os.environ['DB_USERNAME'],
    password=os.environ['DB_PASSWORD'],
    charset='utf8',
    connection_timeout=3600,
    autocommit=True
)
# カーソル取得
db = cnt.cursor(buffered=True)

# role  1 : マーリン、2 : パーシヴァル、3 : ガラハッド、4 : 情弱、
#       9 : モードレッド、10 : モルガナ、 11 : 暗殺者、12 : オベロン
avalon_role = [
[0, 'マーリン'],
[1, 'パーシヴァル'],
[2, 'ガラハッド'],
[3, 'アーサーの忠実なる家来'],
[4, 'アーサーの忠実なる家'],
[5, 'アーサーの忠実なる家来'],
[6, 'アーサーの忠実なる家来'],
[7, 'アーサーの忠実なる家来'],
[8, 'モードレッド'],
[9, 'モルガナ'],
[10, 'モードレッドの手下（暗殺者）'],
[11, 'モードレッドの手下'],
[12, 'オベロン'],
[13, 'モードレッドの手下'],
[14, 'モードレッドの手下'],
[15, 'モードレッドの手下']
]

avalon_role_auto = [
    [0],
    [1],
    [2],
    [3],
    [4],
    [
        [0,1,3,10,11],
        [0,1,3,10,8],
        [0,1,3,10,9],
        [0,1,3,10,12],
        [0,1,3,8,9]
    ],
    [
        [0,1,3,3,10,11],
        [0,1,3,3,10,8],
        [0,1,3,3,10,9],
        [0,1,3,3,10,12],
        [0,1,3,3,8,9]
    ],
    [
        [0,1,3,3,10,11,11],
        [0,1,3,3,10,8,11],
        [0,1,3,3,10,9,11],
        [0,1,3,3,10,8,12],
        [0,1,3,3,10,9,12],
        [0,1,3,3,8,9,10]
    ],
    [
        [0,1,3,3,3,10,11,11],
        [0,1,3,3,3,10,8,11],
        [0,1,3,3,3,10,9,11],
        [0,1,3,3,3,10,8,12],
        [0,1,3,3,3,10,9,12],
        [0,1,3,3,3,8,9,10]
    ],
    [
        [0,1,3,3,3,3,10,11,11],
        [0,1,3,3,3,3,10,8,11],
        [0,1,3,3,3,3,10,9,11],
        [0,1,3,3,3,3,10,8,12],
        [0,1,3,3,3,3,10,9,12],
        [0,1,3,3,3,3,8,9,10]
    ],
    [
        [0,1,3,3,3,3,10,11,11,11],
        [0,1,3,3,3,3,10,12,12,12],
        [0,1,3,3,3,3,10,8,11,12],
        [0,1,3,3,3,3,10,8,12,12],
        [0,1,3,3,3,3,10,9,11,12],
        [0,1,3,3,3,3,10,9,12,12],
        [0,1,3,3,3,3,10,8,9,11],
        [0,1,3,3,3,3,10,8,9,12]
    ]
]
#################################
# Usage文
#################################
# 停止状態 : make -> ゲーム開始待ち
usage_avalon0 ="""
 現在使えるコマンド
   h/help   : ヘルプ（コマンド一覧）
   m/make   : 村作成
"""
# ゲーム開始待ち : start -> ゲーム開始
usage_avalon1="""
 現在使えるコマンド
   h/help   　　　　: ヘルプ（コマンド一覧）
   in/login 　　　　: 村入室
   d/deck 人数  　　: デッキリスト
   ds/deck set 番号: デッキセット
   role            : 役職番号
   s/start  　　    : 開始
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
def role_list(num):
    i=1
    for j in avalon_role_auto[num]:
        role_check = f"役職{i}"
        for k in j:
            if role_check == f"役職{i}":
                role_check = f"{sql}:{avalon_role[k][1]}"
            else:
                role_check = f"{sql}, {avalon_role[k][1]}"
        await ctx.channel.send(f"{role_check}")
        i += 1



@client.event
async def on_ready():
    # テーブル削除
    sql = 'drop table if exists avalon_data'
    db.execute(sql)
    # テーブル削除
    sql = 'drop table if exists avalon_user'
    db.execute(sql)
    # テーブル作成
    sql = "create table if not exists `avalon_data` ( \
    `id` int, \
    `game_status` int, \
    `game_role` int, \
    `quest_cnt` int, \
    `vote_cnt` int, \
    `game_phase` int, \
    `game_stop` int, \
    `game_member_num` int, \
    primary key (`id`) \
    )"
    db.execute(sql)
    # データ挿入
    sql = "insert into `avalon_data` ( \
    `id`, \
    `game_status`, \
    `game_role`, \
    `quest_cnt`, \
    `vote_cnt`, \
    `game_phase`, \
    `game_stop`, \
    `game_member_num` ) \
    value (%s,%s,%s,%s,%s,%s,%s,%s)"
    db.execute(sql, (0,0,0,0,0,0,1,0))
    # テーブル作成
    sql = "create table if not exists `avalon_user` ( \
    `id` int, \
    `name` varchar(255), \
    `user_id` bigint, \
    primary key (`id`) \
    )"
    db.execute(sql)
    sql = 'select * from `avalon_data` where id = 0'
    db.execute(sql)
    rows = db.fetchall()
    for i in rows:
        print(f"データ：{i[1]}, {i[2]}, {i[2]}, {i[3]}, {i[4]}, {i[5]}, {i[6]}")
        print("Logged in as " + client.user.name)

@client.event
async def on_message(ctx):
    try :
        # コネクションが切れた時に再接続してくれるよう設定
        cnt.ping(reconnect=True)
    except mysql.connector.errors.OperationalError:
        await ctx.channel.send(f"もう一度コマンドを入力してください")
        # カーソル終了
        db.close()
        cnt.cursor(buffered=True)

    sql = 'SELECT * FROM `avalon_data` where id = 0'
    db.execute(sql)
    rows = db.fetchall()
    for i in rows:
        game_status=i[1]
        game_role=i[2]
        quest_cnt=i[3]
        vote_cnt=i[4]
        game_phase=i[5]
        game_stop=i[6]
        game_member_num=i[7]

    print(f"現在の状態：game_status = {game_status}, game_role={game_role}, quest_cnt = {quest_cnt}, vote_cnt = {vote_cnt}, game_phase = {game_phase}, game_stop = {game_stop}, game_member_num = {game_member_num}")

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

    # deck number: デッキリスト
    elif ctx.content[0:1] == 'd ' or ctx.content[0:4] == 'deck ':
        if ctx.content[0:1] == 'd ':
            deck_cmd = ctx.content.lstrip("d ")
            try :
                deck_num = int(deck_cmd)
                role_list(deck_num)
            except :
                await ctx.channel.send(f"{ctx.content}コマンドは無効です。")
        elif ctx.content[0:4] == 'deck ':
            deck_cmd = ctx.content.lstrip("deck ")
            try :
                deck_num = int(deck_cmd)
                role_list(deck_num)
            except :
                await ctx.channel.send(f"{ctx.content}コマンドは無効です。")
        else
            await ctx.channel.send(f"{ctx.content}コマンドは無効です。")

    # deck set: デッキ設定
    elif ctx.content[0:2] == 'ds ' or ctx.content[0:8] == 'deck set ':
        if ctx.content[0:2] == 'ds ':
            deck_cmd = ctx.content.lstrip("ds ")
            try :
                game_role = int(deck_cmd)
                sql = f"update `avalon_data` set `game_role`={game_role} where id = 0"
                db.execute(sql)
                await ctx.channel.send(f"デッキを{game_role}に設定しました。")
            except :
                await ctx.channel.send(f"{ctx.content}コマンドは無効です。")
        elif ctx.content[0:8] == 'deck set ':
            deck_cmd = ctx.content.lstrip("deck set ")
            try :
                game_role = int(deck_cmd)
                sql = f"update `avalon_data` set `game_role`={game_role} where id = 0"
                db.execute(sql)
                await ctx.channel.send(f"デッキを{game_role}に設定しました。")
            except :
                await ctx.channel.send(f"{ctx.content}コマンドは無効です。")
        else
            await ctx.channel.send(f"{ctx.content}コマンドは無効です。")

    # start game : ゲームを開始する
    elif ctx.content == 's' or ctx.content == 'start' or ctx.content == 'stop':
        #await ctx.channel.send(f"game_status = {game_status}, command = {ctx.content}")
        if (game_status == 1) and (ctx.content == 's' or ctx.content == 'start'):
            if game_member_num > 4:
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
                await ctx.channel.send("ゲームを開始します。\n配役の公開機能を後で実装します。")
                ary = [['name1', 1, 1], ['name2', 2, 2]]
                for i in range(game_member_num) :
                    sql = f"select * from `avalon_user` where id = {i+1}"
                    #print(sql)
                    db.execute(sql)
                    rows = db.fetchone()
                    num = i + 1
                    #print(rows)
                    for j in rows :
                        #print(j)
                        ary.append([rows[1], rows[2], i+1])
                        break

                random.shuffle(ary)
                # print(ary)
                role = [1, 2, 4, 9, 11]
                # print(role)
                random.shuffle(role)
                # print(role)
                for i in range(game_member_num) :
                    ary[i][2] = role[i]
                # print(ary)

                #msg = client.get_user(user_id[0])
                #await msg.send(f"ゲームを開始します。")
                await ctx.channel.send(f"第{quest_cnt}クエスト、{vote_cnt}回目です。選出してください。")
            else :
                await ctx.channel.send(f"５人以上入室してからゲームを開始してください。\
                \n現在{game_member_num}人です。\
                \nあと{5-game_member_num}以上入室してからsコマンドを実行してください。")
        elif (game_status > 1) and (ctx.content == 's' or ctx.content == 'stop'):
            await ctx.channel.send("stopコマンドのため、ゲーム途中ですが、ゲームを停止します。")
            sql = "update `avalon_data` set \
            `game_status`= 0, \
            `game_role`= 0, \
            `quest_cnt`= 0, \
            `vote_cnt`= 0, \
            `game_phase`= 0, \
            `game_stop`= 1, \
            `game_member_num`= 0"
            db.execute(sql)
            sql = 'drop table avalon_user'
            db.execute(sql)
            # テーブル作成
            sql = "create table if not exists `avalon_user` ( \
            `id` int, \
            `name` varchar(255), \
            `user_id` bigint, \
            primary key (`id`) \
            )"
            db.execute(sql)
        else :
            await ctx.channel.send(f"{ctx.content}コマンドは無効です。")


    # connect check
    # elif ctx.content == 'c':
    #     ary = [[1, 'あき', 100], [2, 'とく', 110], [3, 'いわ', 120], [4, 'ざわ', 130], [5, 'コケ', 140]]
    #     await ctx.channel.send(f"{ary}")
    #     random.shuffle(ary)
    #     await ctx.channel.send(f"{ary}")

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
        sql = "update `avalon_data` set \
        `game_status`= 0, \
        `game_role`= 0, \
        `quest_cnt`= 0, \
        `vote_cnt`= 0, \
        `game_phase`= 0, \
        `game_stop`= 1, \
        `game_member_num`= 0"
        db.execute(sql)
        sql = 'drop table avalon_user'
        db.execute(sql)
        # テーブル作成
        sql = "create table if not exists `avalon_user` ( \
        `id` int, \
        `name` varchar(255), \
        `user_id` bigint, \
        primary key (`id`) \
        )"
        db.execute(sql)
        await ctx.channel.send(f"データを初期化しました。")

    # カーソル終了
    #db.close()
    # MySQL切断
    #cnt.close()

client.run(TOKEN)
