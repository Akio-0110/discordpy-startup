# Work with Python 3.6.6
import os
import re
import random
import asyncio
import discord
import mysql.connector
from mysql.connector import errorcode
from discord import File
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
[0, 'マーリン', './image/マーリン.jpeg'],
[1, 'パーシヴァル', './image/パーシヴァル.jpeg'],
[2, 'ガラハッド', './image/ガラハッド.jpeg'],
[3, 'アーサーの忠実なる家来', './image/情弱１.jpeg'],
[4, 'アーサーの忠実なる家', './image/情弱２.jpeg'],
[5, 'アーサーの忠実なる家来', './image/情弱３.jpeg'],
[6, 'アーサーの忠実なる家来', './image/情弱４.jpeg'],
[7, 'アーサーの忠実なる家来', './image/情弱５.jpeg'],
[8, 'モードレッド', './image/モードレッド.jpeg'],
[9, 'モルガナ', './image/モルガナ.jpeg'],
[10, 'モードレッドの手下（暗殺者）', './image/暗殺者.jpeg'],
[11, 'モードレッドの手下', './image/モードレッドの手下１.jpeg'],
[12, 'オベロン', './image/オベロン.jpeg'],
[13, 'モードレッドの手下', './image/モードレッドの手下１.jpeg'],
[14, 'モードレッドの手下', './image/モードレッドの手下２.jpeg'],
[15, 'モードレッドの手下', './image/モードレッドの手下３.jpeg']
]

avalon_role_auto = [
    [0],
    [1],
    [2],
    [3],
    [4],
    [
        [0,1,3,10,8],
        [0,1,3,10,9],
        [0,1,3,10,11],
        [0,1,3,10,12],
        [0,1,3,8,9]
    ],
    [
        [0,1,3,3,10,8],
        [0,1,3,3,10,9],
        [0,1,3,3,10,11],
        [0,1,3,3,10,12],
        [0,1,3,3,8,9]
    ],
    [
        [0,1,3,3,10,8,11],
        [0,1,3,3,10,9,11],
        [0,1,3,3,10,8,12],
        [0,1,3,3,10,9,12],
        [0,1,3,3,10,11,11],
        [0,1,3,3,8,9,10]
    ],
    [
        [0,1,3,3,3,10,8,11],
        [0,1,3,3,3,10,9,11],
        [0,1,3,3,3,10,8,12],
        [0,1,3,3,3,10,9,12],
        [0,1,3,3,3,10,11,11],
        [0,1,3,3,3,8,9,10]
    ],
    [
        [0,1,3,3,3,3,10,8,11],
        [0,1,3,3,3,3,10,9,11],
        [0,1,3,3,3,3,10,8,12],
        [0,1,3,3,3,3,10,9,12],
        [0,1,3,3,3,3,10,11,11],
        [0,1,3,3,3,3,8,9,10]
    ],
    [
        [0,1,3,3,3,3,10,8,11,12],
        [0,1,3,3,3,3,10,9,11,12],
        [0,1,3,3,3,3,10,8,12,12],
        [0,1,3,3,3,3,10,9,12,12],
        [0,1,3,3,3,3,10,11,11,11],
        [0,1,3,3,3,3,10,12,12,12],
        [0,1,3,3,3,3,10,8,9,11],
        [0,1,3,3,3,3,10,8,9,12]
    ]
]

quest_member_num = [
    [0,0],
    [1,1],
    [2,1],
    [3,1],
    [4,1],
    [
        [2,1],[3,1],[2,1],[3,1],[3,1]
    ],
    [
        [2,1],[3,1],[4,1],[3,1],[4,1]
    ],
    [
        [2,1],[3,1],[3,1],[4,2],[4,1]
    ],
    [
        [2,1],[3,1],[3,1],[4,2],[4,1]
    ],
    [
        [3,1],[4,1],[4,1],[5,2],[5,1]
    ],
    [
        [3,1],[4,1],[4,1],[5,2],[5,1]
    ]
]
#################################
# Usage文
#################################
# 停止状態 : make -> ゲーム開始待ち
usage_avalon0 ="""
   h/help:ヘルプ（コマンド一覧）
   m/make:作成
"""
# ゲーム開始待ち : start -> ゲーム開始
usage_avalon1="""
   h/help:ヘルプ（コマンド一覧）
   in/login:入室
   d/deck 人数:デッキリスト
   ds/deckset 番号:デッキセット
   role:役職
   s/start:開始
"""
usage_avalon20="""
   h/help:ヘルプ（コマンド一覧）
   s/select 数字:選出
   stop:ゲーム停止
"""
usage_avalon21="""
   h/help:ヘルプ（コマンド一覧）
   a/accept:承認
   r/reject:却下
   stop:ゲーム停止
"""
usage_avalon22="""
   h/help:ヘルプ（コマンド一覧）
   s/success:成功
   f/fail:失敗
   stop:ゲーム停止
"""
usage_avalon3="""
   h/help:ヘルプ（コマンド一覧）
   k/kill 数字:暗殺
   stop:ゲーム停止
"""
def role_list_display(num):
    role = 'xxx'
    role_out = [role, role]
    # print(avalon_role_auto[num])
    for j in avalon_role_auto[num]:
        i=1
        for k in j:
            # print(k)
            if i%num == 1:
                role = f"{avalon_role[k][1]}"
            else:
                role = f"{role}\n{avalon_role[k][1]}"
            # print(role)
            if i%num == 0:
                # print(role)
                role_out.append(role)
            i += 1
        # print(role_out)
    role_out.pop(0)
    role_out.pop(0)
    return role_out

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
    `select_member` int, \
    `quest_cnt` int, \
    `vote_cnt` int, \
    `game_phase` int, \
    `game_stop` int, \
    `game_member_num` int, \
    `game_member1` int, \
    `game_member2` int, \
    `game_member3` int, \
    `game_member4` int, \
    `game_member5` int, \
    primary key (`id`) \
    )"
    db.execute(sql)
    # データ挿入
    sql = "insert into `avalon_data` ( \
    `id`, \
    `game_status`, \
    `game_role`, \
    `select_member`, \
    `quest_cnt`, \
    `vote_cnt`, \
    `game_phase`, \
    `game_stop`, \
    `game_member_num` ) \
    value (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    db.execute(sql, (0,0,0,0,0,0,0,1,0))
    # テーブル作成
    sql = "create table if not exists `avalon_user` ( \
    `id` int, \
    `name` varchar(255), \
    `user_id` bigint, \
    `role` int, \
    primary key (`id`) \
    )"
    db.execute(sql)
    # sql = 'select * from `avalon_data` where id = 0'
    # db.execute(sql)
    # rows = db.fetchall()
    # for i in rows:
    print("Logged in as " + client.user.name)

@client.event
async def on_message(ctx):
    comment = ctx.content
    # print(comment[0:1])
    # print(comment[0:2])
    # print(comment[0:3])
    # print(comment[0:4])
    # print(comment[0:5])
    try :
        # コネクションが切れた時に再接続してくれるよう設定
        cnt.ping(reconnect=True)
    except :
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
        select_member=i[3]
        quest_cnt=i[4]
        vote_cnt=i[5]
        game_phase=i[6]
        game_stop=i[7]
        game_member_num=i[8]
        game_member = [i[9],i[10],i[11],i[12],i[13]]

    sql = f"現在の状態：\
    \ngame_status = {game_status}\
    \ngame_role={game_role}\
    \nquest_cnt = {quest_cnt}\
    \nvote_cnt = {vote_cnt}\
    \ngame_phase = {game_phase}\
    \ngame_stop = {game_stop}\
    \ngame_member_num = {game_member_num}"

    if game_member[0] != None:
        sql = f"{sql}\nngame_member = {game_member}"
        print(len(geme_member))

    print(sql)

    # help : ヘルプ
    if comment == 'h' or comment == 'help' or comment == 'ヘルプ':
        if game_status == 0:
            embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon0)
        elif game_status == 1:
            embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon1)
        elif game_status == 2:
            if game_phase == 0:
                embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon20)
            elif game_phase == 1:
                embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon21)
        elif game_status == 3:
            embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon3)
        await ctx.channel.send(embed=embed)

    # status : 状態表示
    if comment == 'status' or comment == '状態':
        sql = '現在の状態は'
        if game_status == 0:
            sql = f"{sql}部屋作成待ち状態です。"
        elif game_status == 1:
            sql = f"{sql}ゲーム開始準備の状態です。\
            \n５人以上の入室(in)と役職(d,ds,role)を選択して、\
            開始コマンド(s)を実行してください。"
        elif game_status == 2:
            if game_phase == 0:
                sql = f"{quest_cnt}クエの{vote_cnt}回目の選出です。"
            elif game_phase == 1:
                sql = f"{quest_cnt}クエの{vote_cnt}回目の選出判定中です。"
            elif game_phase == 2:
                sql = f"{quest_cnt}クエの{vote_cnt}回目のクエスト中です。"
            elif game_phase == 3:
                sql = f"{quest_cnt-1}の乙女選択中です。"
        elif game_status == 3:
            sql = f"{sql}暗殺者の検討中です。"
        await ctx.channel.send(f"{sql}")
        await ctx.channel.send('h')


    if game_status == 0:
        # make : 部屋作成
        if comment == 'm' or comment == 'make' or comment == '作成':
            if game_status == 0:
                sql = f"insert into `avalon_user` (`id`, `name`, `user_id`, `role`) \
                values (%s, %s, %s, %s)"
                val1 = "1"
                val2 = f"{ctx.author.name}"
                val3 = f"{ctx.author.id}"
                db.execute(sql, (val1,val2,val3,'1'))
                sql = f"update `avalon_data` set `game_status`=1 where id = 0"
                db.execute(sql)
                sql = f"update `avalon_data` set `game_member_num`=1 where id = 0"
                db.execute(sql)
                await ctx.channel.send(f"{ctx.author.name}が部屋を作成し、入室しました。 \
                \n現在１人です。\n５人以上集まればゲームを開始できます。")
                embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon1)
                await ctx.channel.send(embed=embed)
            else :
                await ctx.channel.send(f"現在このコマンドは無効です。：{comment}")
    elif game_status == 1:
        # login : 部屋入室
        if comment == 'in' or comment == 'login' or comment == 'ログイン' or comment == '入室':
            if game_status == 1:
                gm_num = game_member_num + 1
                await ctx.channel.send(f"{gm_num}人目:{ctx.author.name}が入室しました。")
                sql = f"update `avalon_data` set `game_member_num` = {gm_num} where id = 0"
                db.execute(sql)
                sql = f"insert into `avalon_user` (`id`, `name`, `user_id`, `role`) \
                values (%s, %s, %s, %s)"
                val1 = f"{gm_num}"
                val2 = f"{ctx.author.name}"
                val3 = f"{ctx.author.id}"
                db.execute(sql, (val1,val2,val3,'1'))
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
                await ctx.channel.send(f"現在このコマンドは無効です。：{comment}")

        # deck number: デッキリスト
        elif comment[0:2] == 'd ' or comment[0:5] == 'deck ' or comment[0:7] == 'デッキリスト ':
            # print(f"xxx{comment[0:2]}xxx")
            # print(f"xxx{comment[0:5]}xxx")
            if game_status == 1:
                if comment[0:2] == 'd ':
                    deck_cmd = comment.lstrip("d ")
                    # try :
                    deck_num = int(deck_cmd)
                    if deck_num > 4 and deck_num < 11 :
                        role = role_list_display(deck_num)
                        for i in range(deck_num):
                            if i == 0:
                                embed = discord.Embed(title=f"役職{i+1}",description=role[i])
                            else:
                                embed.add_field(name=f"役職{i+1}",value=role[i])
                        await ctx.channel.send(embed=embed)
                    else:
                        await ctx.channel.send(f"現在このコマンドは無効です。：{comment}")
                    # except :
                    #     await ctx.channel.send(f"xxx現在このコマンドは無効です。：{comment}")
                elif comment[0:5] == 'deck ':
                    deck_cmd = comment.lstrip("deck ")
                    try :
                        deck_num = int(deck_cmd)
                        if deck_num > 4 and deck_num < 11 :
                            role = role_list_display(deck_num)
                            for i in range(deck_num):
                                if i == 0:
                                    embed = discord.Embed(title=f"役職{i+1}",description=role[i])
                                else:
                                    embed.add_field(name=f"役職{i+1}",value=role[i])
                            await ctx.channel.send(embed=embed)
                        else:
                            await ctx.channel.send(f"現在このコマンドは無効です。：{comment}")
                    except :
                        await ctx.channel.send(f"現在このコマンドは無効です。：{comment}")
                elif comment[0:7] == 'デッキリスト ':
                    deck_cmd = comment.lstrip("デッキリスト ")
                    try :
                        deck_num = int(deck_cmd)
                        if deck_num > 4 and deck_num < 11 :
                            role = role_list_display(deck_num)
                            for i in range(deck_num):
                                if i == 0:
                                    embed = discord.Embed(title=f"役職{i+1}",description=role[i])
                                else:
                                    embed.add_field(name=f"役職{i+1}",value=role[i])
                            await ctx.channel.send(embed=embed)
                        else:
                            await ctx.channel.send(f"現在このコマンドは無効です。：{comment}")
                    except :
                        await ctx.channel.send(f"現在このコマンドは無効です。：{comment}")
                else:
                    await ctx.channel.send(f"現在このコマンドは無効です。：{comment}")
            else :
                await ctx.channel.send(f"現在このコマンドは無効です。：{comment}")

        # deck set: デッキ設定
        elif comment[0:3] == 'ds ' or comment[0:8] == 'deckset ' or comment[0:7] == 'デッキセット ':
            # print(f"xxx{comment[0:3]}xxx")
            # print(f"xxx{comment[0:8]}xxx")
            if game_status == 1:
                if comment[0:3] == 'ds ':
                    deck_cmd = comment.lstrip("ds ")
                    try :
                        game_role = int(deck_cmd)
                        # print(game_role)
                        if game_role >= 0 and game_role <= 7 :
                            sql = f"update `avalon_data` set `game_role`={game_role} where id = 0"
                            await ctx.channel.send(f"デッキを{game_role}に設定しました。")
                        else:
                            await ctx.channel.send(f"現在このコマンドは無効です。：{comment}")
                            sql = f"update `avalon_data` set `game_role`=0 where id = 0"
                            await ctx.channel.send(f"デッキを0に設定しました。")
                        db.execute(sql)
                    except :
                        await ctx.channel.send(f"現在このコマンドは無効です。：{comment}")
                elif comment[0:8] == 'deckset ':
                    deck_cmd = comment.lstrip("deckset ")
                    try :
                        game_role = int(deck_cmd)
                        # print(game_role)
                        if game_role >= 0 and game_role <= 7 :
                            sql = f"update `avalon_data` set `game_role`={game_role} where id = 0"
                            await ctx.channel.send(f"デッキを{game_role}に設定しました。")
                        else:
                            await ctx.channel.send(f"現在このコマンドは無効です。：{comment}")
                            sql = f"update `avalon_data` set `game_role`=0 where id = 0"
                            await ctx.channel.send(f"デッキを0に設定しました。")
                        db.execute(sql)
                    except :
                        await ctx.channel.send(f"現在このコマンドは無効です。：{comment}")
                elif comment[0:7] == 'デッキセット ':
                    deck_cmd = comment.lstrip("デッキセット ")
                    try :
                        game_role = int(deck_cmd)
                        # print(game_role)
                        if game_role >= 0 and game_role <= 7 :
                            sql = f"update `avalon_data` set `game_role`={game_role} where id = 0"
                            await ctx.channel.send(f"デッキを{game_role}に設定しました。")
                        else:
                            await ctx.channel.send(f"現在このコマンドは無効です。：{comment}")
                            sql = f"update `avalon_data` set `game_role`=0 where id = 0"
                            await ctx.channel.send(f"デッキを0に設定しました。")
                        db.execute(sql)
                    except :
                        await ctx.channel.send(f"現在このコマンドは無効です。：{comment}")
                else :
                    await ctx.channel.send(f"現在このコマンドは無効です。：{comment}")
            else :
                await ctx.channel.send(f"現在このコマンドは無効です。：{comment}")

        # role number : 役職カスタマイズ
        elif comment == 'role' or comment == '役職':
            if game_status == 1 :
                for i in range(16):
                    if i == 0:
                        blue_role = f"{avalon_role[i][0]}:{avalon_role[i][1]}"
                    elif i < 4:
                        blue_role = f"{blue_role}\n{avalon_role[i][0]}:{avalon_role[i][1]}"
                        # await ctx.channel.send(f"{avalon_role[i][0]}:青陣営：{avalon_role[i][1]}")
                    elif i == 8:
                        red_role = f"{avalon_role[i][0]}:{avalon_role[i][1]}"
                    elif i > 8 and i <=12:
                        red_role = f"{red_role}\n{avalon_role[i][0]}:{avalon_role[i][1]}"
                embed = discord.Embed(title="青陣営",description=blue_role)
                embed.add_field(name="赤陣営",value=red_role)
                await ctx.channel.send(embed=embed)
                # await ctx.channel.send(f"{avalon_role[i][0]}:赤陣営：{avalon_role[i][1]}")
                embed = discord.Embed(title="コマンド例",description="0:マーリン\n1:パーシヴァル\n3:情弱\n9:モルガナ\n10:暗殺者\nの場合\nrole 0,1,2,9,10\n入室人数に合わせて設定が必要してください。")
                await ctx.channel.send(embed=embed)
            else :
                await ctx.channel.send(f"現在このコマンドは無効です。：{comment}")

        # role number : 役職カスタマイズ
        elif comment[0:5] == 'role ' or comment[0:3] == '役職 ':
            if game_status == 1:
                # if comment[0:3] == '役職 ':
                #     deck_cmd = comment.lstrip("役職 ")
                # elif comment[0:5] == 'role ':
                #     deck_cmd = comment.lstrip("role ")
                deck_cmd_re = re.compile('\d+')
                deck_cmd_match = deck_cmd_re.findall(deck_cmd)
                role_list = [0,1]
                i = 0
                for k in deck_cmd_match:
                    if (k != None):
                        if i < 2 :
                            role_list[i] = int(k)
                        else :
                            role_list.append(int(k))
                        i = i + 1

                # print(role_list)
                # print(deck_cmd_match)
                for k in range(game_member_num):
                    sql = f"update `avalon_user` set `role`={role_list[k]} where id = {k}"
                    db.execute(sql)
                    if k == 0:
                        sql_role = f"{avalon_role[role_list[k]][1]}"
                    else:
                        sql_role = f"{sql_role}\n{avalon_role[role_list[k]][1]}"
                #print(sql)
                await ctx.channel.send(f"デッキをカスタマイズしました")
                embed = discord.Embed(title="選択役職",description=sql_role)
                await ctx.channel.send(embed=embed)
            else :
                await ctx.channel.send(f"現在このコマンドは無効です。：{comment}")

        # start game : ゲームを開始する
        elif comment == 's' or comment == 'start' or comment == '開始':
            #await ctx.channel.send(f"game_status = {game_status}, command = {comment}")
            if game_member_num > 4:
                sql = f"update `avalon_data` set `game_status`=2 where id = 0"
                db.execute(sql)
                quest_cnt = 1
                sql = f"update `avalon_data` set `quest_cnt`={quest_cnt} where id = 0"
                db.execute(sql)
                vote_cnt = 1
                sql = f"update `avalon_data` set `vote_cnt`={vote_cnt} where id = 0"
                db.execute(sql)
                ary = [['name1', 1, 1], ['name2', 2, 2]]
                if  game_member_num == 5:
                    user_id = [10,10,10,10,10]
                    role = [0, 1, 3, 8, 10]
                elif  game_member_num == 6:
                    user_id = [10,10,10,10,10,10]
                    role = [0, 1, 3, 3, 8, 10]
                elif  game_member_num == 6:
                    user_id = [10,10,10,10,10,10,10]
                    role = [0, 1, 3, 3, 8, 9, 10]
                elif  game_member_num == 6:
                    user_id = [10,10,10,10,10,10,10,10]
                    role = [0, 1, 3, 3, 3, 8, 9, 10]
                elif  game_member_num == 6:
                    user_id = [10,10,10,10,10,10,10,10,10]
                    role = [0, 1, 3, 3, 3, 3, 8, 9, 10]
                elif  game_member_num == 6:
                    user_id = [10,10,10,10,10,10,10,10,10,10]
                    role = [0, 1, 3, 3, 3, 3, 8, 9, 10, 12]

                for i in range(game_member_num) :
                    sql = f"select * from `avalon_user` where id = {i+1}"
                    #print(sql)
                    db.execute(sql)
                    rows = db.fetchone()
                    #print(rows)
                    for j in rows :
                        #print(j)
                        ary.append([rows[1], rows[2], rows[3]])
                        # name[i] = rows[1]
                        user_id[i] = rows[2]
                        role[i] = rows[3]
                        break

                # print(ary)
                # print(ary.pop(0))
                # print(ary.pop(0))
                ary.pop(0)
                ary.pop(0)
                random.shuffle(ary)
                # print(ary)
                # print(f"game_role = {game_role}")
                # print(role)

                for i in range(game_member_num) :
                    if game_role == 999:
                        role[i] = ary[i][2]
                    else:
                        role[i] = avalon_role_auto[game_member_num][game_role-1][i]

                # print(role)
                random.shuffle(role)
                # print(role)
                for i in range(game_member_num) :
                    ary[i][2] = role[i]
                # print(ary)

                for i in range(game_member_num) :
                    sql = f"update `avalon_user` set \
                    `name` = {ary[i][0]},\
                    `user_id` = {ary[i][1]},\
                    `role` = {ary[i][2]}\
                     where id = {i+1}"
                    db.execute(sql)

                # print(role)
                # print(ary)
                for i in range(game_member_num):
                    msg = client.get_user(user_id[i])
                    await msg.send(f"あなたの役職は{avalon_role[role[i]][1]}です。", file=File(f"{avalon_role[role[i]][2]}"))
                    if role[i] == 0 : # マーリン
                        role_info = '赤陣営は\n'
                        for j in range(game_member_num):
                            if (role[j] >= 9):
                                role_info = f"{role_info}{ary[j][0]}\n"
                        role_info = f"{role_info}です。\nバレないようにクエスト勝利へ導いてください。"
                        await msg.send(f"{role_info}")
                    elif role[i] == 1 : # パーシヴァル
                        role_info = 'マーリンとモルガナを確認することができます。\n'
                        for j in range(game_member_num):
                            if (role[j] == 0 or role[j] == 9):
                                role_info = f"{role_info}{ary[j][0]}\n"
                        role_info = f"{role_info}がマーリンとモルガナです。\n役職によって１人とは限りません。"
                        await msg.send(f"{role_info}")
                    elif role[i] == 2 : # ガラハッド
                        role_info = f"{role_info}パーシヴァルと暗殺者を確認することができます。\n"
                        for j in range(game_member_num):
                            if (role[j] == 1 or role[j] == 10):
                                role_info = f"{role_info}{ary[j][0]}\n"
                        role_info = f"{role_info}がパーシヴァルと暗殺者です。\n役職によって2人とは限りません。"
                        await msg.send(f"{role_info}")
                    elif role[i] >= 8 and role[i] <= 11 : # 赤陣営
                        role_info = '赤陣営は\n'
                        for j in range(game_member_num):
                            if (role[j] >= 8 and role[j] <= 11):
                                role_info = f"{role_info}{ary[j][0]}\n"
                        role_info = f"{role_info}です。"
                        await msg.send(f"{role_info}")

                    # await msg.send(f"あなたの役職は{avalon_role[role[i]][1]}です。\n{file:{attachment:{avalon_role[i][2]}}}")
                await ctx.channel.send('ゲームを開始します。')
                await ctx.channel.send('status')
            else :
                await ctx.channel.send(f"現在このコマンドは無効です。：{comment}\
                \n現在の入室人数は{game_member_num}人です。\
                \nあと{5-game_member_num}以上入室してからsコマンドを実行してください。")

    elif game_status == 2:
        user_ary = [[1, 'name1', 1, 1], [2, 'name2', 2, 2]]
        for i in range(game_member_num) :
            sql = f"select * from `avalon_user` where id = {i+1}"
            #print(sql)
            db.execute(sql)
            rows = db.fetchone()
            #print(rows)
            for j in rows :
                #print(j)
                user_ary.append([rows[0], rows[1], rows[2], rows[3]])
                break

        user_ary.pop(0)
        user_ary.pop(0)

        if comment == 'stop' or comment == '停止':
            await ctx.channel.send("stopコマンドのため、ゲーム途中ですが、ゲームを停止します。")
            sql = "update `avalon_data` set \
            `game_status`= 0, \
            `game_role`= 0, \
            `quest_cnt`= 0, \
            `vote_cnt`= 0, \
            `game_phase`= 0, \
            `game_stop`= 1, \
            `game_member_num`= 0 \
            `game_member1`= NULL \
            `game_member1`= NULL \
            `game_member1`= NULL \
            `game_member1`= NULL \
            `game_member1`= NULL"
            db.execute(sql)
            sql = 'drop table avalon_user'
            db.execute(sql)
            # テーブル作成
            sql = "create table if not exists `avalon_user` ( \
            `id` int, \
            `name` varchar(255), \
            `user_id` bigint, \
            `role` int, \
            primary key (`id`) \
            )"
            db.execute(sql)
            await ctx.channel.send('status')

        if game_phase == 0: #選出フェーズ
            # start game : ゲームを開始する
            if comment[0:2] == 's ' or comment[0:7] == 'select ' or comment[0:3] == '選択 ':
                if game_phase == 0:
                    select_member = re.compile('\d+')
                    select_member_match = deck_cmd_re.findall(select_member)
                    if len(select_member_match) != quest_member_num[game_member_num][quest_cnt-1][0]:
                        await ctx.channel.send(f"現在このコマンドは無効です。：{comment}\
                        \n選出人数は{quest_member_num[{game_member_num}][{quest_cnt-1}]}人です。")
                    else :
                        select_list = [0,1]
                        i = 0
                        for k in select_member_match:
                            if (k != None):
                                if i < 2 :
                                    select_list[i] = int(k)
                                else :
                                    select_list.append(int(k))
                                i = i + 1
                        i = 1
                        for i in range(game_member_num) :
                            sql = f"update `avalon_data` set `select_member{i}` = \
                            NULL where id = 0"
                            db.execute(sql)
                            i = i + 1

                        i = 1
                        for k in select_list:
                            if k != None:
                                sql = f"update `avalon_data` set `select_member{i}` = \
                                {select_list[i-1]} where id = 0"
                                db.execute(sql)
                                i = i + 1
                        game_phase = 1
                        sql = f"update `avalon_data` set `game_phase` = {game_phase} where id = 0"
                        db.execute(sql)
                        for i in range(len(select_list)):
                            if i != None:
                                if i == 0:
                                    user_name = f"{user_ary[i][0]}:{user_ary[i][1]}"
                                else:
                                    user_name = f"{user_name}\n{user_ary[i][0]}:{user_ary[i][1]}"

                        embed = discord.Embed(title="選出メンバー",description=f"{user_name}\
                        \n選出メンバーでクエストへ出発したい場合:承認(a/accept)\
                        \n選出メンバーでクエストへ出発したくない場合:却下(r/reject)\
                        \nしてください")
                        await ctx.channel.send(embed=embed)
                else:
                    await ctx.channel.send(f"現在このコマンドは無効です。：{comment}\n\
                    現在メンバー選出フェーズではありません。")

        elif game_phase == 1: #承認却下フェーズ
            if comment == 'a' or comment == 'accept' or comment == '承認':
                await ctx.channel.send("投票を受け付けました。")
            elif comment == 'r' or comment == 'reject' or comment == '却下':
                await ctx.channel.send("投票を受け付けました。")

        elif game_phase == 2: #承認却下フェーズ
            if comment == 's' or comment == 'success' or comment == '成功':
                await ctx.channel.send("投票を受け付けました。")
            elif comment == 'f' or comment == 'fail' or comment == '失敗':
                await ctx.channel.send("投票を受け付けました。")

    # connect check
    # elif comment == 'c':
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
    # init : 初期化
    if comment == 'i' or comment == 'init':
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
        `role` int, \
        primary key (`id`) \
        )"
        db.execute(sql)
        await ctx.channel.send(f"データを初期化しました。")

#        embed = discord.Embed()
#        embed.set_image(url=f"avalon_role[0][2]")
        # await ctx.channel.send("マーリン",file=File(f"{avalon_role[0][2]}"))
        # await ctx.channel.send(file=f"avalon_role[0][2]")


    # カーソル終了
    #db.close()
    # MySQL切断
    #cnt.close()

client.run(TOKEN)
