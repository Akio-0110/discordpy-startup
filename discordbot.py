# Work with Python 3.6.6
import os
import re
import glob
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
[8, 'アーサーの忠実なる家来', './image/情弱５.jpeg'],
[9, 'アーサーの忠実なる家来', './image/情弱５.jpeg'],
[10, 'モードレッド', './image/モードレッド.jpeg'],
[11, 'モルガナ', './image/モルガナ.jpeg'],
[12, 'モードレッドの手下（暗殺者）', './image/暗殺者.jpeg'],
[13, 'モードレッドの手下', './image/モードレッドの手下１.jpeg'],
[14, 'オベロン', './image/オベロン.jpeg'],
[15, 'モードレッドの手下', './image/モードレッドの手下１.jpeg'],
[16, 'モードレッドの手下', './image/モードレッドの手下２.jpeg'],
[17, 'モードレッドの手下', './image/モードレッドの手下３.jpeg'],
[17, 'モードレッドの手下', './image/モードレッドの手下３.jpeg'],
[17, 'モードレッドの手下', './image/モードレッドの手下３.jpeg']
]

avalon_role_auto = [
    [0],
    [1],
    [2],
    [3],
    [4],
    [
        [0,1,3,12,10],
        [0,1,3,12,11],
        [0,1,3,12,13],
        [0,1,3,12,14],
        [0,1,3,10,11]
    ],
    [
        [0,1,3,3,12,10],
        [0,1,3,3,12,11],
        [0,1,3,3,12,13],
        [0,1,3,3,12,14],
        [0,1,3,3,10,11]
    ],
    [
        [0,1,3,3,12,10,13],
        [0,1,3,3,12,11,13],
        [0,1,3,3,12,10,14],
        [0,1,3,3,12,11,14],
        [0,1,3,3,12,13,13],
        [0,1,3,3,10,11,12]
    ],
    [
        [0,1,3,3,3,12,10,13],
        [0,1,3,3,3,12,11,13],
        [0,1,3,3,3,12,10,14],
        [0,1,3,3,3,12,11,14],
        [0,1,3,3,3,12,13,13],
        [0,1,3,3,3,10,11,12]
    ],
    [
        [0,1,3,3,3,3,12,10,13],
        [0,1,3,3,3,3,12,11,13],
        [0,1,3,3,3,3,12,10,14],
        [0,1,3,3,3,3,12,11,14],
        [0,1,3,3,3,3,12,13,13],
        [0,1,3,3,3,3,10,11,12]
    ],
    [
        [0,1,3,3,3,3,12,10,13,14],
        [0,1,3,3,3,3,12,11,13,14],
        [0,1,3,3,3,3,12,10,14,14],
        [0,1,3,3,3,3,12,11,14,14],
        [0,1,3,3,3,3,12,13,13,13],
        [0,1,3,3,3,3,12,14,14,14],
        [0,1,3,3,3,3,12,10,11,13],
        [0,1,3,3,3,3,12,10,11,14]
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
usage_avalon23="""
h/help:ヘルプ（コマンド一覧）
e/excalibur 番号:エクスカリバー
stop:ゲーム停止
"""
usage_avalon24="""
h/help:ヘルプ（コマンド一覧）
s/survey 番号:調査
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

def player_display(member_num, ary, select_member):
    # print(ary)
    if select_member == 0:
        sql = f"■ 1:{ary[0][1]}"
    else:
        sql = f"□ 1:{ary[0][1]}"

    for i in range(member_num):
        if i == 0: continue
        elif i == select_member:
            sql = f"{sql}\n■ {i+1}:{ary[i][1]}"
        else:
            sql = f"{sql}\n□ {i+1}:{ary[i][1]}"
    return sql


def player_role_display(member_num, ary):
    # print(ary)
    sql = f"{ary[0][1]}:{avalon_role[ary[0][3]][1]}"
    for i in range(member_num):
        if i == 0: continue
        sql = f"{sql}\n{ary[i][1]}:{avalon_role[ary[i][3]][1]}"

    return sql

@client.event
async def on_ready():

    try :
        # コネクションが切れた時に再接続してくれるよう設定
        cnt.ping(reconnect=True)
    except :
        print(f"データベースの再接続をします。\nもう一度コマンドを入力してください")
        # カーソル終了
        db.close()
        cnt.cursor(buffered=True)

    # テーブル削除
    sql = 'drop table if exists avalon_data'
    db.execute(sql)
    sql = 'drop table if exists avalon_user'
    db.execute(sql)
    sql = 'drop table if exists avalon_quest'
    db.execute(sql)
    # テーブル作成
    sql = "create table if not exists `avalon_data` ( \
    `id` int, \
    `channel_id` bigint, \
    `game_status` int, \
    `game_role` int, \
    `select_member` int, \
    `quest_cnt` int, \
    `quest_success_cnt` int, \
    `quest_fail_cnt` int, \
    `vote_cnt` int, \
    `game_phase` int, \
    `game_stop` int, \
    `game_member_num` int, \
    `game_otome` int, \
    `game_excalibur` int, \
    `game_member1` int, \
    `game_member2` int, \
    `game_member3` int, \
    `game_member4` int, \
    `game_member5` int, \
    `game_otome1` int, \
    `game_otome2` int, \
    `game_otome3` int, \
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
    `quest_success_cnt`, \
    `quest_fail_cnt`, \
    `vote_cnt`, \
    `game_phase`, \
    `game_stop`, \
    `game_member_num`, \
    `game_otome`, \
    `game_excalibur` ) \
    value (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    db.execute(sql, (0,0,1,0,0,0,0,0,0,1,0,0,0))
    # テーブル作成 ユーザ情報
    sql = "create table if not exists `avalon_user` ( \
    `id` int, \
    `name` varchar(255), \
    `user_id` bigint, \
    `role` int, \
    primary key (`id`) \
    )"
    db.execute(sql)
    print("Logged in as " + client.user.name)

@client.event
async def on_message(ctx):
    if ctx.author != client.user:
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
            game_status=i[2]
            game_role=i[3]
            select_member=i[4]
            quest_cnt=i[5]
            quest_success_cnt=i[6]
            quest_fail_cnt=i[7]
            vote_cnt=i[8]
            game_phase=i[9]
            game_stop=i[10]
            game_member_num=i[11]
            game_otome=i[12]
            game_excalibur=i[13]
            if game_status == 2 and game_phase != 0:
                game_member = [i[14],i[15],i[16],i[17],i[18]]
                game_otome1 = i[19]
                game_otome2 = i[20]
                game_otome3 = i[21]
            if game_status >= 1:
                channel_id = i[1]
            break

        sql = f"現在の状態：\
        \ngame_status = {game_status}\
        \ngame_role = {game_role}\
        \nselect_member = {select_member}\
        \nquest_cnt = {quest_cnt}\
        \nquest_success_cnt = {quest_success_cnt}\
        \nquest_fail_cnt = {quest_fail_cnt}\
        \nvote_cnt = {vote_cnt}\
        \ngame_phase = {game_phase}\
        \ngame_stop = {game_stop}\
        \ngame_member_num = {game_member_num}\
        \ngame_otome = {game_otome}\
        \ngame_excalibur = {game_excalibur}"

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
                elif game_phase == 2:
                    embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon22)
                elif game_phase == 3:
                    embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon23)
                elif game_phase == 4:
                    embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon24)
            elif game_status == 3:
                embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon3)
            await ctx.channel.send(embed=embed)

        if game_status == 0:
            # make : 部屋作成
            if comment == 'm' or comment == 'make' or comment == '作成':
                if game_status == 0:
                    sql = 'drop table if exists avalon_data'
                    db.execute(sql)
                    sql = 'drop table if exists avalon_user'
                    db.execute(sql)
                    sql = 'drop table if exists avalon_quest'
                    db.execute(sql)
                    # テーブル作成
                    sql = "create table if not exists `avalon_data` ( \
                    `id` int, \
                    `channel_id` bigint, \
                    `game_status` int, \
                    `game_role` int, \
                    `select_member` int, \
                    `quest_cnt` int, \
                    `quest_success_cnt` int, \
                    `quest_fail_cnt` int, \
                    `vote_cnt` int, \
                    `game_phase` int, \
                    `game_stop` int, \
                    `game_member_num` int, \
                    `game_otome` int, \
                    `game_excalibur` int, \
                    `game_member1` int, \
                    `game_member2` int, \
                    `game_member3` int, \
                    `game_member4` int, \
                    `game_member5` int, \
                    `game_otome1` int, \
                    `game_otome2` int, \
                    `game_otome3` int, \
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
                    `quest_success_cnt`, \
                    `quest_fail_cnt`, \
                    `vote_cnt`, \
                    `game_phase`, \
                    `game_stop`, \
                    `game_member_num`, \
                    `game_otome`, \
                    `game_excalibur` ) \
                    value (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    db.execute(sql, (0,0,1,0,0,0,0,0,0,1,0,0,0))
                    # テーブル作成 ユーザ情報
                    sql = "create table if not exists `avalon_user` ( \
                    `id` int, \
                    `name` varchar(255), \
                    `user_id` bigint, \
                    `role` int, \
                    primary key (`id`) \
                    )"
                    db.execute(sql)
                    sql = f"insert into `avalon_user` (`id`, `name`, `user_id`, `role`) \
                    values (%s, %s, %s, %s)"
                    val1 = "1"
                    val2 = f"{ctx.author.display_name}"
                    val3 = f"{ctx.author.id}"
                    db.execute(sql, (val1,val2,val3,'1'))
                    sql = f"update `avalon_data` set `game_status`=1 where id = 0"
                    db.execute(sql)
                    sql = f"update `avalon_data` set `game_member_num`=1 where id = 0"
                    db.execute(sql)
                    sql = f"update `avalon_data` set `channel_id`={ctx.channel.id} where id = 0"
                    db.execute(sql)
                    await ctx.channel.send(f"{ctx.author.display_name}が部屋を作成し、入室しました。 \
                    \n現在１人です。\n５人以上集まればゲームを開始できます。")
                    embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon1)
                    await ctx.channel.send(embed=embed)
                else :
                    await ctx.channel.send(f"現在このコマンドは無効です。：{comment}")

        elif game_status == 1:
            msgch = client.get_channel(channel_id)
            # login : 部屋入室
            if comment == 'in' or comment == 'login' or comment == 'ログイン' or comment == '入室':
                if game_member_num < 10:
                    gm_num = game_member_num + 1
                    if gm_num < 5:
                        await msgch.send(f"{gm_num}人目:{ctx.author.display_name}が入室しました。")
                    else:
                        await msgch.send(f"{gm_num}人目:{ctx.author.display_name}が入室しました。\n5人以上入室したため、開始コマンド(s)でゲームを開始することができます。")
                    sql = f"update `avalon_data` set `game_member_num` = {gm_num} where id = 0"
                    db.execute(sql)
                    sql = f"insert into `avalon_user` (`id`, `name`, `user_id`, `role`) \
                    values (%s, %s, %s, %s)"
                    val1 = f"{gm_num}"
                    val2 = f"{ctx.author.display_name}"
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
                else:
                    await msgch.send(f"満室です。")

            # deck number: デッキリスト
            elif comment[0:2] == 'd ' or comment[0:5] == 'deck ' or comment[0:7] == 'デッキリスト ':
                if comment[0:2] == 'd ':
                    deck_cmd = comment.lstrip("d ")
                    # try :
                    deck_num = int(deck_cmd)
                    if deck_num > 4 and deck_num < 11 :
                        role = role_list_display(deck_num)
                        for i in range(len(role)):
                            if i == 0:
                                embed = discord.Embed(title=f"役職{i+1}",description=role[i])
                            else:
                                embed.add_field(name=f"役職{i+1}",value=role[i])
                        await msgch.send(embed=embed)
                    else:
                        await msgch.send(f"現在このコマンドは無効です。：{comment}")
                    # except :
                    #     await msgch.send(f"xxx現在このコマンドは無効です。：{comment}")
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
                            await msgch.send(embed=embed)
                        else:
                            await msgch.send(f"現在このコマンドは無効です。：{comment}")
                    except :
                        await msgch.send(f"現在このコマンドは無効です。：{comment}")
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
                            await msgch.send(embed=embed)
                        else:
                            await msgch.send(f"現在このコマンドは無効です。：{comment}")
                    except :
                        await msgch.send(f"現在このコマンドは無効です。：{comment}")

            # deck set: デッキ設定
            elif comment[0:3] == 'ds ' or comment[0:8] == 'deckset ' or comment[0:7] == 'デッキセット ':
                if comment[0:3] == 'ds ':
                    deck_cmd = comment.lstrip("ds ")
                    try :
                        game_role = int(deck_cmd)
                        # print(game_role)
                        # print(avalon_role_auto[game_member_num])
                        if game_role > 0 and game_role <= len(avalon_role_auto[game_member_num]) :
                            sql = f"update `avalon_data` set `game_role`={game_role} where id = 0"
                            await msgch.send(f"デッキを{game_role}に設定しました。")
                        else:
                            await msgch.send(f"現在このコマンドは無効です。：{comment}")
                            sql = f"update `avalon_data` set `game_role`=1 where id = 0"
                            await msgch.send(f"デッキを1に設定しました。")
                        db.execute(sql)
                    except :
                        await msgch.send(f"現在このコマンドは無効です。：{comment}")
                elif comment[0:8] == 'deckset ':
                    deck_cmd = comment.lstrip("deckset ")
                    try :
                        game_role = int(deck_cmd)
                        # print(game_role)
                        if game_role > 0 and game_role <= len(avalon_role_auto[game_member_num]) :
                            sql = f"update `avalon_data` set `game_role`={game_role} where id = 0"
                            await msgch.send(f"デッキを{game_role}に設定しました。")
                        else:
                            await msgch.send(f"現在このコマンドは無効です。：{comment}")
                            sql = f"update `avalon_data` set `game_role`=0 where id = 0"
                            await msgch.send(f"デッキを0に設定しました。")
                        db.execute(sql)
                    except :
                        await msgch.send(f"現在このコマンドは無効です。：{comment}")
                elif comment[0:7] == 'デッキセット ':
                    deck_cmd = comment.lstrip("デッキセット ")
                    try :
                        game_role = int(deck_cmd)
                        # print(game_role)
                        if game_role >= 0 and game_role <= 7 :
                            sql = f"update `avalon_data` set `game_role`={game_role} where id = 0"
                            await msgch.send(f"デッキを{game_role}に設定しました。")
                        else:
                            await msgch.send(f"現在このコマンドは無効です。：{comment}")
                            sql = f"update `avalon_data` set `game_role`=0 where id = 0"
                            await msgch.send(f"デッキを0に設定しました。")
                        db.execute(sql)
                    except :
                        await msgch.send(f"現在このコマンドは無効です。：{comment}")

            # role number : 役職カスタマイズ
            elif comment == 'role' or comment == '役職':
                for i in range(16):
                    if i == 0:
                        blue_role = f"{avalon_role[i][0]}:{avalon_role[i][1]}"
                    elif i < 4:
                        blue_role = f"{blue_role}\n{avalon_role[i][0]}:{avalon_role[i][1]}"
                        # await msgch.send(f"{avalon_role[i][0]}:青陣営：{avalon_role[i][1]}")
                    elif i == 10:
                        red_role = f"{avalon_role[i][0]}:{avalon_role[i][1]}"
                    elif i >= 11 and i <=14:
                        red_role = f"{red_role}\n{avalon_role[i][0]}:{avalon_role[i][1]}"
                embed = discord.Embed(title="青陣営",description=blue_role)
                embed.add_field(name="赤陣営",value=red_role)
                embed.add_field(name="コマンド例",value="0:マーリン\n1:パーシヴァル\n3:情弱\n11:モルガナ\n12:暗殺者\nの場合\nrole 0,1,2,11,12\n入室人数に合わせて設定が必要してください。")
                await msgch.send(embed=embed)

            # role number : 役職カスタマイズ
            elif comment[0:5] == 'role ' or comment[0:3] == '役職 ':
                deck_cmd_re = re.compile('\d+')
                deck_cmd_match = deck_cmd_re.findall(comment)
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
                    sql = f"update `avalon_user` set `role`={role_list[k]} where id = {k+1}"
                    db.execute(sql)
                    if k == 0:
                        sql_role = f"{avalon_role[role_list[k]][1]}"
                    else:
                        sql_role = f"{sql_role}\n{avalon_role[role_list[k]][1]}"
                #print(sql)

                sql = f"update `avalon_data` set `game_role`= 999 where id = 0"
                db.execute(sql)
                await msgch.send(f"デッキをカスタマイズしました")
                embed = discord.Embed(title="選択役職",description=sql_role)
                await msgch.send(embed=embed)

                # sql = f"select role from `avalon_user`"
                # db.execute(sql)
                # rows = db.fetchall()
                # print(rows)

            # otome : 乙女設定
            elif comment == 'o' or comment == 'otome' or comment == '乙女':
                if game_otome == 0:
                    game_otome = 1
                else:
                    game_otome = 0
                sql = f"update `avalon_data` set `game_otome` = {game_otome} where id =0"
                db.execute(sql)
                if game_otome == 1:
                    op_msg = "乙女を有効にしました。\n無効にする場合、もう一度コマンドを入力してください。"
                else:
                    op_msg = "乙女を無効にしました。\n有効にする場合、もう一度コマンドを入力してください。"
                embed = discord.Embed(title="オプション設定",description=op_msg)
                await msgch.send(embed=embed)
            # otome : エクスカリバー設定
            elif comment == 'e' or comment == 'excalibur' or comment == 'エクスカリバー':
                if game_excalibur == 0:
                    game_excalibur = 1
                else:
                    game_excalibur = 0
                sql = f"update `avalon_data` set `game_excalibur` = {game_excalibur} where id =0"
                db.execute(sql)
                if game_excalibur == 1:
                    op_msg = "エクスカリバーを有効にしました。\n無効にする場合、もう一度コマンドを入力してください。"
                else:
                    op_msg = "エクスカリバーを無効にしました。\n有効にする場合、もう一度コマンドを入力してください。"
                embed = discord.Embed(title="オプション設定",description=op_msg)
                await msgch.send(embed=embed)

            # start game : ゲームを開始する
            elif comment == 's' or comment == 'start' or comment == '開始':
                #await msgch.send(f"game_status = {game_status}, command = {comment}")
                if game_member_num > 4:
                    sql = f"update `avalon_data` set `game_status`=2 where id = 0"
                    db.execute(sql)
                    quest_cnt = 1
                    sql = f"update `avalon_data` set `quest_cnt`={quest_cnt} where id = 0"
                    db.execute(sql)
                    vote_cnt = 1
                    sql = f"update `avalon_data` set `vote_cnt`={vote_cnt} where id = 0"
                    db.execute(sql)
                    if game_otome == 1:
                        game_otome1 = game_member_num - 1
                        sql = f"update `avalon_data` set `game_otome1`={game_otome1} where id = 0"
                        db.execute(sql)
                    ary = [[1,'name1', 1, 1], [2, 'name2', 2, 2]]
                    if  game_member_num == 5:
                        user_id = [10,10,10,10,10]
                        role = [0, 1, 3, 8, 10]
                    elif  game_member_num == 6:
                        user_id = [10,10,10,10,10,10]
                        role = [0, 1, 3, 3, 8, 10]
                    elif  game_member_num == 7:
                        user_id = [10,10,10,10,10,10,10]
                        role = [0, 1, 3, 3, 8, 9, 10]
                    elif  game_member_num == 8:
                        user_id = [10,10,10,10,10,10,10,10]
                        role = [0, 1, 3, 3, 3, 8, 9, 10]
                    elif  game_member_num == 9:
                        user_id = [10,10,10,10,10,10,10,10,10]
                        role = [0, 1, 3, 3, 3, 3, 8, 9, 10]
                    elif  game_member_num == 10:
                        user_id = [10,10,10,10,10,10,10,10,10,10]
                        role = [0, 1, 3, 3, 3, 3, 8, 9, 10, 12]

                    for i in range(game_member_num) :
                        sql = f"select * from `avalon_user` where id = {i+1}"
                        db.execute(sql)
                        rows = db.fetchone()
                        ary.append([rows[0], rows[1], rows[2], rows[3]])
                        user_id[i] = rows[2]
                        # print(rows[3])
                        role[i] = rows[3]

                    # print(role)
                    ary.pop(0)
                    ary.pop(0)
                    random.shuffle(ary)

                    for i in range(game_member_num) :
                        if game_role != 999:
                            role[i] = avalon_role_auto[game_member_num][game_role-1][i]

                    # print(role)
                    random.shuffle(role)
                    # print(role)
                    for i in range(game_member_num) :
                        ary[i][3] = role[i]
                    # print(ary)

                    for i in range(game_member_num) :
                        num = i + 1
                        sql = f"update `avalon_user` set \
                        `name` = '{ary[i][1]}',\
                        `user_id` = {ary[i][2]},\
                        `role` = {ary[i][3]} \
                        where id = {i+1}"
                        # print(sql)
                        db.execute(sql)

                    # print(role)
                    # print(ary)

                    for i in range(game_member_num):
                        msg = client.get_user(user_id[i])
                        await msg.send(f"あなたの役職は{avalon_role[role[i]][1]}です。", file=File(f"{avalon_role[role[i]][2]}"))
                        if role[i] == 0 : # マーリン
                            role_info = '赤陣営は\n'
                            for j in range(game_member_num):
                                if (role[j] >= 11):
                                    role_info = f"{role_info}{ary[j][1]}\n"
                            role_info = f"{role_info}です。\nバレないようにクエスト勝利へ導いてください。"
                            await msg.send(f"{role_info}")
                        elif role[i] == 1 : # パーシヴァル
                            role_info = 'マーリンとモルガナを確認することができます。\n'
                            for j in range(game_member_num):
                                if (role[j] == 0 or role[j] == 11):
                                    role_info = f"{role_info}{ary[j][1]}\n"
                            role_info = f"{role_info}がマーリンとモルガナです。\n役職によって１人とは限りません。"
                            await msg.send(f"{role_info}")
                        elif role[i] == 2 : # ガラハッド
                            role_info = f"{role_info}パーシヴァルと暗殺者を確認することができます。\n"
                            for j in range(game_member_num):
                                if (role[j] == 1 or role[j] == 12):
                                    role_info = f"{role_info}{ary[j][1]}\n"
                            role_info = f"{role_info}がパーシヴァルと暗殺者です。\n役職によって2人とは限りません。"
                            await msg.send(f"{role_info}")
                        elif role[i] >= 10 and role[i] <= 13 : # 赤陣営
                            role_info = '赤陣営は\n'
                            for j in range(game_member_num):
                                if (role[j] >= 10 and role[j] <= 13):
                                    role_info = f"{role_info}{ary[j][1]}\n"
                            role_info = f"{role_info}です。"
                            await msg.send(f"{role_info}")

                        # await msg.send(f"あなたの役職は{avalon_role[role[i]][1]}です。\n{file:{attachment:{avalon_role[i][2]}}}")
                    await msgch.send('ゲームを開始します。')

                    sql = player_display(game_member_num, ary, select_member)
                    embed = discord.Embed(title=f"第{quest_cnt}クエスト：{vote_cnt}回目の選出:\nリーダは{ary[select_member][1]}です。\n{quest_member_num[game_member_num][quest_cnt-1][0]}人選出してください",description=sql)
                    await msgch.send(embed=embed)

                    # テーブル作成
                    sql = "create table `avalon_quest` ( `id` int,"
                    for i in range(game_member_num):
                        sql = f"{sql} `member{i+1}` int,"
                    sql = f"{sql} primary key (`id`) )"
                    # print(sql)
                    db.execute(sql)


                else :
                    await msgch.send(f"現在このコマンドは無効です。：{comment}\
                    \n現在の入室人数は{game_member_num}人です。\
                    \nあと{5-game_member_num}以上入室してからsコマンドを実行してください。")

        elif game_status == 2:
            msgch = client.get_channel(channel_id)
            quest_id = int((quest_cnt-1)*5+vote_cnt)
            avalon_user = [[1, 'name1', 1, 1], [1, 'name2', 2, 2]]
            for i in range(game_member_num) :
                sql = f"select * from `avalon_user` where id = {i+1}"
                db.execute(sql)
                rows = db.fetchone()
                avalon_user.append([0, rows[1], rows[2], rows[3]])
            avalon_user.pop(0)
            avalon_user.pop(0)
            # print(avalon_user)

            if game_phase != 0:
                sql = f"select * from `avalon_quest` where id = {int((quest_cnt-1)*5+vote_cnt)}"
                db.execute(sql)
                rows = db.fetchone()
                avalon_quest = [1]*game_member_num
                # print(avalon_quest)
                # print(rows)
                for i in range(game_member_num):
                    # print(rows[i+1])
                    avalon_quest[i] = int(rows[i])
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
            # print(user_ary)

            if comment == 'stop' or comment == '停止':
                await msgch.send("stopコマンドのため、ゲーム途中ですが、ゲームを停止します。")
                sql = "update `avalon_data` set \
                `game_status`= 0, \
                `game_role`= 1, \
                `quest_cnt`= 0, \
                `quest_success_cnt` = 0, \
                `quest_fail_cnt` = 0, \
                `vote_cnt`= 0, \
                `game_phase`= 0, \
                `game_stop`= 1, \
                `game_member_num`= 0, \
                `game_member1`= NULL, \
                `game_member2`= NULL, \
                `game_member3`= NULL, \
                `game_member4`= NULL, \
                `game_member5`= NULL, \
                `game_otome1` = NULL, \
                `game_otome2` = NULL, \
                `game_otome3` = NULL"
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
                await msgch.send('status')

            elif game_phase == 0: #選出フェーズ
                # start game : ゲームを開始する
                if comment[0:2] == 's ' or comment[0:7] == 'select ' or comment[0:3] == '選択 ':
                    if ctx.author.id == avalon_user[select_member][2]:
                        if game_member_num == 5:
                            quest_data = [0,0,0,0,0]
                        elif game_member_num == 6:
                            quest_data = [0,0,0,0,0,0]
                        elif game_member_num == 7:
                            quest_data = [0,0,0,0,0,0,0]
                        elif game_member_num == 8:
                            quest_data = [0,0,0,0,0,0,0,0]
                        elif game_member_num == 9:
                            quest_data = [0,0,0,0,0,0,0,0,0]
                        elif game_member_num == 10:
                            quest_data = [0,0,0,0,0,0,0,0,0,0]
                        select_member_com = re.compile('\d+')
                        select_member_match = select_member_com.findall(comment)
                        # 重複チェック
                        if len(select_member_match) == len(set(select_member_match)):
                            if len(select_member_match) != quest_member_num[game_member_num][quest_cnt-1][0]:
                                await msgch.send(f"現在このコマンドは無効です。：{comment}\
                                \n選出人数は{quest_member_num[game_member_num][quest_cnt-1][0]}人です。")
                            else :
                                select_list = [0,1]
                                range_in = 1
                                i = 0
                                for k in select_member_match:
                                    if (k != None):
                                        if int(k) == 0 or int(k) > game_member_num:
                                            range_in = 0
                                        if range_in == 1:
                                            if i < 2 :
                                                select_list[i] = int(k)
                                                quest_data[select_list[i]-1] = 1
                                            else :
                                                select_list.append(int(k))
                                                quest_data[select_list[i]-1] = 1
                                            i = i + 1

                                if range_in == 1:
                                    sql = "insert into `avalon_quest` ( `id` ,"
                                    for i in range(game_member_num):
                                        if i < game_member_num - 1:
                                            sql = f"{sql} `member{i+1}`,"
                                        else:
                                            sql = f"{sql} `member{i+1}` ) value ("

                                    for i in range(game_member_num+1):
                                        if i < game_member_num:
                                            sql = f"{sql}%s,"
                                        else:
                                            sql = f"{sql}%s)"

                                    quest_data.insert(0, int((quest_cnt-1)*5+vote_cnt))
                                    db.execute(sql, quest_data)

                                    i = 1
                                    for k in select_list:
                                        if k != None:
                                            sql = f"update `avalon_data` set `game_member{i}` = \
                                            {select_list[i-1]} where id = 0"
                                            db.execute(sql)
                                            i = i + 1

                                    game_phase = 1
                                    sql = f"update `avalon_data` set `game_phase` = {game_phase} where id = 0"
                                    db.execute(sql)
                                    for i in range(len(select_list)):
                                        if i != None:
                                            if i == 0:
                                                user_name = f"{user_ary[select_list[i]-1][0]}:{user_ary[select_list[i]-1][1]}"
                                            else:
                                                user_name = f"{user_name}\n{user_ary[select_list[i]-1][0]}:{user_ary[select_list[i]-1][1]}"

                                    if vote_cnt != 5:
                                        embed = discord.Embed(title="選出メンバー",description=f"{user_name}\n承認 : a/accept\n却下 : r/reject")
                                    else:
                                        embed = discord.Embed(title="選出メンバー",description=f"{user_name}\n承認 : a/accept\n却下 : r/reject\nこの選出が却下された場合、赤陣営の勝利です。")
                                    await msgch.send(embed=embed)
                                else:
                                    await msgch.send(f"選出番号は1〜{game_member_num}から選んでください。：{comment}")
                        else:
                            await msgch.send(f"重複しないメンバー選出をお願いします。：{comment}")
                    else:
                        await msgch.send(f"あなたは選出リーダではありません。")

            elif game_phase == 1: #承認却下フェーズ
                command_accept = 0
                if comment == 'a' or comment == 'accept' or comment == 'r' or comment == 'reject' or comment == '承認' or comment == '却下':
                    if comment == 'a' or comment == 'accept' or comment == '承認':
                        command_accept = 4
                    elif comment == 'r' or comment == 'reject' or comment == '却下':
                        command_accept = 2

                    for i in range(game_member_num):
                        if ctx.author.id == avalon_user[i][2]:
                            msg = client.get_user(user_ary[i][2])
                            if avalon_quest[i] < 2:
                                sql = f"update `avalon_quest` \
                                set `member{i+1}` = {avalon_quest[i]+command_accept} \
                                where id = {quest_id}"
                                avalon_quest[i] = avalon_quest[i] + command_accept
                                for k in range(game_member_num):
                                    if k == 0:
                                        if avalon_quest[k] > 1 or i == k:
                                            vote_msg = f"1 : {avalon_user[k][1]} : 投票完了"
                                        else:
                                            vote_msg = f"1 : {avalon_user[k][1]} : 投票未完"
                                    else:
                                        if avalon_quest[k] > 1 or i == k:
                                            vote_msg = f"{vote_msg}\n{k+1} : {avalon_user[k][1]} : 投票完了"
                                        else:
                                            vote_msg = f"{vote_msg}\n{k+1} : {avalon_user[k][1]} : 投票未完"
                                if command_accept == 2:
                                    await msg.send(f"却下を受け付けました。")
                                else:
                                    await msg.send(f"承認を受け付けました。")

                                embed = discord.Embed(title="投票状況",description=vote_msg)
                                await msgch.send(embed=embed)
                            else:
                                sql = f"update `avalon_quest` \
                                set `member{i+1}` = {avalon_quest[i]%2+command_accept} \
                                where id = {quest_id}"
                                avalon_quest[i] = avalon_quest[i]%2 + command_accept
                                if command_accept == 2:
                                    await msg.send(f"却下へ上書きしました。")
                                else:
                                    await msg.send(f"承認へ上書きしました。")
                            # print(avalon_quest)
                            # print(sql)
                            db.execute(sql)
                            # break

                    # judge next phase
                    reject_cnt = 0
                    accept_cnt = 0
                    vote_msg = f"第{quest_cnt}クエスト：{vote_cnt}回目"
                    for i in range(game_member_num):
                        if avalon_quest[i] > 1:
                            if avalon_quest[i] == 2 or avalon_quest[i] == 3:
                                reject_cnt += 1
                                vote_msg = f"{vote_msg}\n{i+1} : {avalon_user[i][1]} : 却下"
                            elif avalon_quest[i] == 4 or avalon_quest[i] == 5:
                                accept_cnt += 1
                                vote_msg = f"{vote_msg}\n{i+1} : {avalon_user[i][1]} : 承認"
                        else:
                            break
                        if i == game_member_num-1:
                            select_member = int((select_member+1)%game_member_num)
                            # 承認
                            if accept_cnt > reject_cnt:
                                game_phase = 2
                                sql = f"update `avalon_data` set \
                                `game_phase`= {game_phase} \
                                where id = 0"
                                # print(sql)
                                db.execute(sql)
                                embed = discord.Embed(title="投票結果",description=f"{vote_msg}\n個人メッセージで\n成功の場合:s\n失敗の場合:f\nを実行してください")
                                file = "./image/承認.jpeg"
                                await msgch.send(embed=embed, file=File(f"{file}"))
                            # 却下
                            else:
                                if vote_cnt != 5:
                                    game_phase = 0
                                    vote_cnt += 1
                                    sql = f"update `avalon_data` set \
                                    `game_phase`= {game_phase}, \
                                    `select_member`= {select_member}, \
                                    `vote_cnt` = {vote_cnt} \
                                    where id = 0"
                                    # print(sql)
                                    db.execute(sql)
                                    embed = discord.Embed(title="投票結果",description=f"{vote_msg}")
                                    file = "./image/却下.jpeg"
                                    sql = player_display(game_member_num, avalon_user, select_member)
                                    if vote_cnt == 5:
                                        sql = f"{sql}\n次の選出が却下された場合、赤陣営の勝利です。"
                                    embed.add_field(name=f"第{quest_cnt}クエスト：{vote_cnt}回目の選出:\nリーダは{avalon_user[select_member][1]}です。\n{quest_member_num[game_member_num][quest_cnt-1][0]}人選出してください\n３人選出例：s 1,2,3",value=sql)
                                    await msgch.send(embed=embed, file=File(f"{file}"))
                                else:
                                    sql = "update `avalon_data` set \
                                    `game_status` = 0, \
                                    `game_role` = 1, \
                                    `select_member` = 0, \
                                    `quest_cnt` = 0, \
                                    `vote_cnt` = 0, \
                                    `game_phase` = 0, \
                                    `game_stop` = 1, \
                                    `game_member_num` = 0 where id = 0"
                                    db.execute(sql)
                                    sql = player_role_display(game_member_num, avalon_user)
                                    embed = discord.Embed(title="ゲーム終了",description=f"選出が5回却下されたため赤陣営の勝利です。\n{sql}")
                                    await msgch.send(embed=embed)

            elif game_phase == 2: #成功失敗フェーズ
                command_accept = 0
                if comment == 's' or comment == 'success' or comment == '成功' or comment == 'f' or comment == 'fail' or comment == '失敗':
                    if comment == 's' or comment == 'success' or comment == '成功':
                        command_accept = 16
                    elif comment == 'f' or comment == 'fail' or comment == '失敗':
                        command_accept = 8

                    for i in range(quest_member_num[game_member_num][quest_cnt-1][0]):
                        num = game_member[i]-1
                        if ctx.author.id == avalon_user[num][2]:
                            msg = client.get_user(user_ary[num][2])
                            if avalon_quest[num] < 8:
                                sql = f"update `avalon_quest` \
                                set `member{num+1}` = {avalon_quest[num]+command_accept} \
                                where id = {quest_id}"
                                avalon_quest[num] = avalon_quest[num] + command_accept

                                for k in range(quest_member_num[game_member_num][quest_cnt-1][0]):

                                    if k == 0:
                                        if avalon_quest[num] > 8 or game_member[k]-1 == num:
                                            vote_msg = f"投票完了:{game_member[k]}:{avalon_user[game_member[k]-1][1]}"
                                        else:
                                            vote_msg = f"投票未完:{game_member[k]}:{avalon_user[game_member[k]-1][1]}"
                                    else:
                                        if avalon_quest[num] > 8 or game_member[k]-1 == num:
                                            vote_msg = f"{vote_msg}\n投票完了:{game_member[k]}:{avalon_user[game_member[k]-1][1]}"
                                        else:
                                            vote_msg = f"{vote_msg}\n投票未完:{game_member[k]}:{avalon_user[game_member[k]-1][1]}"

                                if command_accept == 16:
                                    await msg.send(f"成功を受け付けました。")
                                else:
                                    await msg.send(f"失敗を受け付けました。")

                            else:
                                sql = f"update `avalon_quest` \
                                set `member{i+1}` = {avalon_quest[i]%2+command_accept} \
                                where id = {quest_id}"
                                avalon_quest[i] = avalon_quest[i]%2 + command_accept
                                if command_accept == 16:
                                    await msg.send(f"成功へ上書きしました。")
                                else:
                                    await msg.send(f"失敗へ上書きしました。")
                            # print(avalon_quest)
                            # print(sql)
                            db.execute(sql)
                            # break
                    embed = discord.Embed(title="投票状況",description=vote_msg)
                    await msgch.send(embed=embed)

                    # judge next phase
                    fail_cnt = 0
                    success_cnt = 0
                    vote_msg = f"第{quest_cnt}クエスト："
                    member_msg = "クエスト参加メンバー"
                    for i in range(quest_member_num[game_member_num][quest_cnt-1][0]):
                        num = game_member[i]-1
                        if avalon_quest[num] > 8:
                            if avalon_quest[num] < 16:
                                fail_cnt += 1
                            else:
                                success_cnt += 1
                        else:
                            break
                        if i == quest_member_num[game_member_num][quest_cnt-1][0]-1:
                            select_member = int((select_member+1)%game_member_num)
                            for k in range(success_cnt+fail_cnt):
                                member_msg = f"{member_msg}\n{avalon_user[num][0]} : {avalon_user[num][1]}"
                                if k < success_cnt:
                                    vote_msg = f"{vote_msg}\n成功"
                                else:
                                    vote_msg = f"{vote_msg}\n失敗"
                            # 成功失敗判断
                            if quest_cnt == 4 and game_member_num >= 7 and game_member_num <= 10:
                                base_num = 2
                            else:
                                base_num = 1

                            if fail_cnt >= base_num:
                                quest_fail_cnt += 1
                                file = './image/クエスト失敗.jpeg'
                                embed = discord.Embed(title="投票結果:失敗",description=f"{vote_msg}\n{member_msg}")
                            else:
                                quest_success_cnt += 1
                                file = './image/クエスト成功.jpeg'
                                embed = discord.Embed(title="投票結果:成功",description=f"{vote_msg}\n{member_msg}")

                            if quest_success_cnt == 3:
                                game_phase = 0
                                quest_cnt += 1
                                vote_cnt = 1
                                for k in range(game_member_num):
                                    if avalon_user[k][3] == 0:
                                        kill_flag = 1
                                        break

                                if kill_flag == 1:
                                    sql = f"update `avalon_data` set \
                                    `game_status`= 3, \
                                    `game_role`= 1, \
                                    `quest_cnt`= 0, \
                                    `quest_success_cnt` = 0, \
                                    `quest_fail_cnt` = 0, \
                                    `vote_cnt`= 0, \
                                    `game_phase`= 0, \
                                    `game_stop`= 0, \
                                    `game_member1`= NULL, \
                                    `game_member2`= NULL, \
                                    `game_member3`= NULL, \
                                    `game_member4`= NULL, \
                                    `game_member5`= NULL, \
                                    `game_otome1` = NULL, \
                                    `game_otome2` = NULL, \
                                    `game_otome3` = NULL \
                                    where id = 0"
                                    db.execute(sql)
                                    for k in range(game_member_num):
                                        if k == 0:
                                            for j in range(game_member_num):
                                                if avalon_user[j][3] == 10:
                                                    msg = client.get_user(avalon_user[j][2])
                                            sql = "暗殺者の方はマーリンを予想してください"
                                        sql = f"{sql}\n{k+1} : {avalon_user[k][1]}"
                                    await msg.send(sql)
                                    embed.add_field(name=f"クエスト：青陣営勝利", value="暗殺者の方はマーリンを予想してください。")
                                    await msgch.send(embed=embed, file=File(f"{file}"))
                                else:
                                    sql = f"update `avalon_data` set \
                                    `game_status`= 0, \
                                    `game_role`= 1, \
                                    `quest_cnt`= 0, \
                                    `quest_success_cnt` = 0, \
                                    `quest_fail_cnt` = 0, \
                                    `vote_cnt`= 0, \
                                    `game_phase`= 0, \
                                    `game_stop`= 1, \
                                    `game_member_num`= 0, \
                                    `game_member1`= NULL, \
                                    `game_member2`= NULL, \
                                    `game_member3`= NULL, \
                                    `game_member4`= NULL, \
                                    `game_member5`= NULL, \
                                    `game_otome1` = NULL, \
                                    `game_otome2` = NULL, \
                                    `game_otome3` = NULL \
                                    where id = 0"
                                    db.execute(sql)
                                    sql = "配役は以下の通りです。"
                                    for i in range(game_member_num):
                                        sql = f"{sql}\n{i+1} : {avalon_user[i][1]} : {avalon_role[avalon_user[i][3]][1]}"
                                    embed.add_field(name=f"クエスト：青陣営勝利",value=f"{sql}")
                                    await msgch.send(embed=embed, file=File(f"{file}"))
                            elif quest_fail_cnt == 3:
                                game_phase = 0
                                quest_cnt += 1
                                vote_cnt = 1
                                sql = f"update `avalon_data` set \
                                `game_status`= 0, \
                                `game_role`= 1, \
                                `quest_cnt`= 0, \
                                `quest_success_cnt` = 0, \
                                `quest_fail_cnt` = 0, \
                                `vote_cnt`= 0, \
                                `game_phase`= 0, \
                                `game_stop`= 1, \
                                `game_member_num`= 0, \
                                `game_member1`= NULL, \
                                `game_member2`= NULL, \
                                `game_member3`= NULL, \
                                `game_member4`= NULL, \
                                `game_member5`= NULL, \
                                `game_otome1` = NULL, \
                                `game_otome2` = NULL, \
                                `game_otome3` = NULL \
                                where id = 0"
                                db.execute(sql)
                                sql = "配役は以下の通りです。"
                                for i in range(game_member_num):
                                    sql = f"{sql}\n{i+1} : {avalon_user[i][1]} : {avalon_role[avalon_user[i][3]][1]}"
                                embed.add_field(name=f"クエスト：赤陣営勝利", value=f"{sql}")
                                await msgch.send(embed=embed, file=File(f"{file}"))
                            else:
                                if game_otome == 1 and (quest_cnt >= 2 and quest_cnt <= 4):
                                    game_phase = 4
                                    sql = f"update `avalon_data` set \
                                    `game_phase`= {game_phase}, \
                                    `quest_success_cnt` = {quest_success_cnt}, \
                                    `quest_fail_cnt` = {quest_fail_cnt} \
                                    where id = 0"
                                    db.execute(sql)
                                    otome_select = [game_otome1, game_otome2, game_otome3]
                                    embed.add_field(name=f"第{quest_cnt}クエスト終了",value=f"{avalon_user[otome_select[quest_cnt-2]][1]}が乙女選出者中です。")
                                    await msgch.send(embed=embed, file=File(f"{file}"))
                                    sql = player_display(game_member_num, avalon_user, select_member)
                                    embed = discord.Embed(title="乙女選出",description=f"{sql}\n乙女選出者は{avalon_user[otome_select[quest_cnt-2]][1]}です。\n選出例:\ns/select/選出 番号です。")
                                    await msg.send(embed=embed)
                                else:
                                    game_phase = 0
                                    quest_cnt += 1
                                    vote_cnt = 1
                                    sql = f"update `avalon_data` set \
                                    `game_phase`= {game_phase}, \
                                    `select_member`= {select_member}, \
                                    `quest_cnt`= {quest_cnt}, \
                                    `quest_success_cnt` = {quest_success_cnt}, \
                                    `quest_fail_cnt` = {quest_fail_cnt}, \
                                    `vote_cnt` = {vote_cnt} \
                                    where id = 0"
                                    db.execute(sql)
                                    sql = player_display(game_member_num, avalon_user, select_member)
                                    embed.add_field(name=f"第{quest_cnt}クエスト：{vote_cnt}回目の選出:\nリーダは{avalon_user[select_member][1]}です。\n{quest_member_num[game_member_num][quest_cnt-1][0]}人選出してください",value=sql)
                                    await msgch.send(embed=embed, file=File(f"{file}"))

            elif game_phase == 4: #乙女フェーズ
                otome_select = [game_otome1, game_otome2, game_otome3]
                if comment[0:2] == 's ' or comment[0:7] == 'survey ' or comment[0:3] == '調査 ':
                    if ctx.author.id == avalon_user[otome_select[quest_cnt-2]][2]:
                        select_member_com = re.compile('\d+')
                        select_member_match = select_member_com.findall(comment)
                        # print(select_member_match)
                        # 重複チェック
                        if len(select_member_match) != 1:
                            await ctx.author.send(f"選択人数は1人です：{comment}")
                        else :
                            otome_check = 0
                            otome_num = int(select_member_match[0])-1
                            # print("コマンドを受け付けました。")
                            # print(int(select_member_match[0]))
                            # print(f"otome_num = {otome_num}")
                            # print(f"quest_cnt-1 = {quest_cnt-1}")
                            for i in range(quest_cnt-1):
                                # print(otome_select[i])
                                if otome_select[i] == None:
                                    break
                                elif otome_num == otome_select[i]:
                                    await ctx.author.send(f"乙女使用者は選出できません。")
                                    otome_check = otome_check + 1
                                    break

                            print(f"otome_check={otome_check}")
                            if otome_check == 0 and otome_num >= 0 and otome_num < game_member_num:
                                msg = client.get_user(avalon_user[otome_num][2])
                                if avalon_user[otome_num][3] < 10:
                                    otome_msg = f"{avalon_user[otome_num][1]}は青陣営です"
                                    file="./image/忠誠カード青.jpeg"
                                else:
                                    otome_msg = f"{avalon_user[otome_num][1]}は赤陣営です"
                                    file="./image/忠誠カード赤.jpeg"
                                embed = discord.Embed(title="乙女結果",description=otome_msg)
                                await msg.send(embed=embed, file=File(f"{file}"))
                                # await msgch.send(f"乙女を{avalon_user[otome_num][1]}に使用しました。")
                                game_phase = 0
                                quest_cnt += 1
                                vote_cnt = 1
                                select_member += 1
                                sql = f"update `avalon_data` set \
                                `game_phase`= {game_phase}, \
                                `select_member`= {select_member}, \
                                `quest_cnt`= {quest_cnt}, \
                                `vote_cnt` = {vote_cnt} \
                                where id = 0"
                                db.execute(sql)
                                sql = player_display(game_member_num, avalon_user, select_member)
                                embed.add_field(name=f"第{quest_cnt}クエスト：{vote_cnt}回目の選出:\nリーダは{avalon_user[select_member][1]}です。\n{quest_member_num[game_member_num][quest_cnt-1][0]}人選出してください",value=sql)
                                await msgch.send(f"乙女を{avalon_user[otome_num][1]}に使用しました。", embed=embed)
                            else:
                                await msg.send(f"選択番号は1〜{game_member_num}にしてください")
                    else:
                        await msgch.send(f"あなた({ctx.author.display_name})は選出リーダではありません。")

        elif game_status == 3:
            msgch = client.get_channel(channel_id)
            quest_id = int((quest_cnt-1)*5+vote_cnt)
            avalon_user = [[1, 'name1', 1, 1], [1, 'name2', 2, 2]]
            for i in range(game_member_num) :
                sql = f"select * from `avalon_user` where id = {i+1}"
                db.execute(sql)
                rows = db.fetchone()
                avalon_user.append([0, rows[1], rows[2], rows[3]])
            avalon_user.pop(0)
            avalon_user.pop(0)

            # kill : 暗殺
            if comment[0:2] == 'k ' or comment[0:5] == 'kill ' or comment[0:3] == '暗殺 ':
                for i in range(game_member_num):
                    if avalon_user[i][3] == 12:
                        kill_member = i
                        break

                if kill_member == None:
                    for i in range(game_member_num):
                        if avalon_user[i][3] == 10:
                            kill_member = i
                            break

                if kill_member == None:
                    for i in range(game_member_num):
                        if avalon_user[i][3] == 10:
                            kill_member = i
                            break

                msg = client.get_user(avalon_user[kill_member][2])
                if ctx.author.id == avalon_user[kill_member][2]:
                    select_member = re.compile('\d+')
                    select_member_match = select_member.findall(comment)
                    if len(select_member_match) != 1:
                        msg.send("暗殺メンバーは１人です。")
                    else:
                        if int(select_member_match[0]) >= 1 and int(select_member_match[0]) <= game_member_num:
                            sql = "配役は以下の通りです。"
                            for i in range(game_member_num):
                                sql = f"{sql}\n{i+1} : {avalon_user[i][1]} : {avalon_role[avalon_user[i][3]][1]}"

                            select_member_num = int(select_member_match[0])
                            if avalon_user[select_member_num-1][3] == 0:
                                kill_msg = "見事マーリンを当てました。"
                                embed = discord.Embed(title="暗殺成功:赤陣営の勝利",description=f"{kill_msg}\n{sql}")
                            else:
                                kill_msg = "マーリンを暗殺できませんでした。"
                                embed = discord.Embed(title="暗殺失敗:青陣営の勝利",description=f"{kill_msg}\n{sql}")
                            await msgch.send(embed=embed)
                            sql = "update `avalon_data` set \
                            `game_status`= 0, \
                            `game_role`= 1, \
                            `quest_cnt`= 0, \
                            `quest_success_cnt` = 0, \
                            `quest_fail_cnt` = 0, \
                            `vote_cnt`= 0, \
                            `game_phase`= 0, \
                            `game_stop`= 1, \
                            `game_member_num`= 0, \
                            `game_member1`= NULL, \
                            `game_member2`= NULL, \
                            `game_member3`= NULL, \
                            `game_member4`= NULL, \
                            `game_member5`= NULL, \
                            `game_otome1` = NULL, \
                            `game_otome2` = NULL, \
                            `game_otome3` = NULL \
                            where id = 0"
                            db.execute(sql)
                        else:
                            msg.send(f"暗殺メンバーは１〜{game_member_num}で選択してください。")

        # status : 状態表示
        if comment == '?' or comment == '？' or comment == '状態':
            if game_status == 0:
                sql = f"部屋作成待ち状態です。\nゲームを始めるには部屋を作成してください。\nコマンド：m/make/作成"
                embed = discord.Embed(title=f"現在の状況",description=sql)
                await ctx.channel.send(embed=embed)
            elif game_status == 1:
                sql = f"ゲーム開始準備の状態です。\
                \n５人以上の入室(in)と役職(d,ds,role)を選択して、\
                開始コマンド(s)を実行してください。"
                embed = discord.Embed(title=f"現在の状況",description=sql)
                await msgch.send(embed=embed)
            elif game_status == 2:
                if game_phase == 0:
                    sql = f"{quest_cnt}クエの{vote_cnt}回目の選出です。"
                elif game_phase == 1:
                    sql = f"{quest_cnt}クエの{vote_cnt}回目の選出判定中です。"
                elif game_phase == 2:
                    sql = f"{quest_cnt}クエの{vote_cnt}回目のクエスト中です。"
                elif game_phase == 3:
                    sql = f"{quest_cnt-1}の乙女選択中です。"
                sql = f"{sql}\n{player_display(game_member_num, avalon_user, select_member)}"
                embed = discord.Embed(title=f"第{quest_cnt}クエスト：{vote_cnt}回目の選出:\nリーダは{avalon_user[select_member][1]}です。\n{quest_member_num[game_member_num][quest_cnt-1][0]}人選出してください\n３人選出例：s 1,2,3",description=sql)
                await msgch.send(embed=embed)
            elif game_status == 3:
                sql = f"{sql}暗殺フェーズです。"
                embed = discord.Embed(title=f"現在の状況",description=sql)
                await msgch.send(embed=embed)

        # init : 初期化
        elif comment == 'i' or comment == 'init':
            sql = "update `avalon_data` set \
            `game_status`= 0, \
            `game_role`= 1, \
            `quest_cnt`= 0, \
            `quest_success_cnt` = 0, \
            `quest_fail_cnt` = 0, \
            `vote_cnt`= 0, \
            `game_phase`= 0, \
            `game_stop`= 1, \
            `game_otome` = 0, \
            `game_excalibur` = 0, \
            `game_member_num`= 0, \
            `game_member1`= NULL, \
            `game_member2`= NULL, \
            `game_member3`= NULL, \
            `game_member4`= NULL, \
            `game_member5`= NULL, \
            `game_otome1` = NULL, \
            `game_otome2` = NULL, \
            `game_otome3` = NULL \
            where id = 0"
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

        # init : 初期化
        elif comment == 'c':
            print(glob.glob("./image/*"))
            otome_msg = f"赤陣営です"
            file="./image/忠誠カード赤.jpeg"
            embed = discord.Embed(title="乙女結果",description=otome_msg)
            await ctx.channel.send(embed=embed, file=File(f"{avalon_role[0][2]}"))

client.run(TOKEN)
