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
from discord.ext import tasks
from datetime import datetime
# from tkinter import messagebox

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

avalon_role = [
[0, 'マーリン', './image/マーリン.jpeg', '陣営：青陣営\nマーリンはモードレッドを覗く赤陣営を知っています。\nただし、クエスト成功後の暗殺で殺害されると青陣営の負けになります。\n\nアグラヴェインがいる場合、アグラヴェインも赤陣営として知りません。\n※ローカル拡張役職です。'],
[1, 'パーシヴァル', './image/パーシヴァル.jpeg', '陣営：青陣営\nパーシヴァルはマーリンとモルガナを知っています。'],
[2, 'ガラハッド', './image/ガラハッド.jpeg', '陣営：青陣営\nガラハッドはパーシヴァルと暗殺者とクエスティングビーストを知っています。\n※ローカル拡張役職です。'],
[3, 'アーサーの忠実なる家来', './image/情弱１.jpeg', '陣営：青陣営\nアーサーの忠実なる家来は何も情報を持っていません。'],
[4, 'ボールス(未対応)', './image/ボールス.jpeg', '陣営：青陣営\nボールスはゲーム中に「邪悪はついに特定された！」と自分の役職を公開し、赤陣営の配役を当てることができれば暗殺フェーズへ移ります。\nただし失敗した場合、その後の選出リーダと投票権を失います。\n※ローカル拡張役職です。'],
[5, 'エクター・ド・マリス(未対応)', './image/エクター.jpeg', '陣営：青陣営\nエクター・ド・マリスはゲーム中に「邪悪よ、覚悟せよ！」と自分の役職を公開し、他のプレイヤー1人の忠誠を確認した上で捉えるか選択できます。\n捕らえられたプレイヤーはその後のリーダーと投票権を失います。\nまたオープンした時点で自身のリーダと投票権を失います。\n※ローカル拡張役職です。'],
[6, 'カラドック', './image/カラドック.jpeg', '陣営：青陣営\nカラドックはマーリンに赤陣営として通知されます。\n※ローカル拡張役職です。'],
[7, 'ガウェイン', './image/ガウェイン.jpeg', '陣営：青陣営\nガウェインはクエスト２とクエスト４に参加した場合、失敗しか出すことができません。\n※ローカル拡張役職です。'],
[8, 'トリスタンとイゾルデ', './image/トリスタンとイゾルデ.jpeg', '陣営：青陣営\nトリスタンとイゾルデは恋人同士でお互いを知っています。\nただしクエストに二人で参加しない場合、失敗しか出すことができません。\n暗殺フェーズにて、マーリンの代わりに暗殺対象になることがあります。\n暗殺対象は暗殺者が選択します。\n※ローカル拡張役職です。'],
[9, None, None, None],
[10, 'モードレッド', './image/モードレッド.jpeg', '陣営：赤陣営\nモードレッドはマーリンから見えません。\n青陣営になりすましましょう。'],
[11, 'モルガナ', './image/モルガナ.jpeg', '陣営：赤陣営\nモルガナはパーシヴァルから見られます。\nパーシヴァルにマーリンと思ってもらうようプレイしましょう。'],
[12, 'モードレッドの手下（暗殺者）', './image/暗殺者.jpeg', '陣営：赤陣営\n暗殺者は青陣営がクエストを3回成功させた場合に、メンバーの1人を暗殺します。\nマーリンを暗殺できれば赤陣営が逆転勝利します。\n\n※ローカル拡張役職ありの場合：\n1)トリスタンとイゾルデがいる場合、恋人同士であるトリスタンとイゾルデの2人を指定することでも勝利します。\n2)ガラハッドがいる場合には、ガラハッドに知られます。'],
[13, 'モードレッドの手下', './image/モードレッドの手下１.jpeg', '陣営：赤陣営\nモードレッドの手下は何も能力を持っていません。'],
[14, 'オベロン', './image/オベロン.jpeg', '陣営：赤陣営\nオベロンは仲間の赤陣営を知りません。'],
[15, 'アグラヴェイン', './image/アグラヴェイン.jpeg', '陣営：赤陣営\nアグラヴェインはマーリンに赤陣営と知られません。\nまた赤陣営のプレイヤーを知っていますが、他の赤陣営には知られません。\n2回成功するまで失敗を出すことができません。\n※ローカル拡張役職です。'],
[16, 'クエスティングビースト', './image/クエスティングビースト.jpeg', '陣営：赤陣営\nクエスティングビーストはゲーム開始時に1人のプレイヤーを選択し、オベロンにします。\nこの時に選んだプレイヤーの役職を知ります。選ばれたプレイヤーの役職は失われるが、マーリンだった場合に限り、パーシヴァルがマーリンとなります。\nまたガラハッドからパーシヴァルと一緒に知られます。\n※ローカル拡張役職です。'],
[17, None, None, None],
[18, None, None, None],
[19, None, None, None],
[20, 'ロット王(未対応)', './image/ロット.jpeg', '陣営：青陣営または赤陣営または陣営無\nロット王は2回目の失敗が出た直後に任意のプレイヤー1人を選択し、そのプレイヤーと同じ陣営となります。\n選ばれたプレイヤーは明かされるが、ロット王が誰かは知られません。\n陣営が決まる前にクエストが終了すると敗北です。\n陣営が決まるまで成功でも失敗でも出すことができます。\n※ローカル拡張役職です。'],
[21, 'ケイ', './image/ケイ.jpeg', '陣営：青陣営または赤陣営\nケイは奇数クエストでは青陣営、偶数クエストでは赤陣営です。\n偶数クエストでクエストに参加した場合、失敗しか出すことができません。\nゲーム終了時の陣営に従って勝利条件も変わります。\n４クエストで終了した場合、暗殺議論に加わってください。\n※ローカル拡張役職です。'],
[22, 'ランスロット(未対応)', './image/モードレッドの手下２.jpeg', '不明'],
[23, None, None, None],
[24, None, None, None],
[25, None, None, None],
[26, None, None, None],
[27, None, None, None],
[28, None, None, None],
[29, None, None, None],
[30, 'シャロット姫', './image/シャロット姫.jpeg', '陣営：第３陣営\nシャロット姫は役職に関係なく赤陣営全員を知っています。\n暗殺されると単独勝利します。赤陣営のクエスト勝利時は敗北となります。\n※ローカル拡張役職です。'],
[31, '漁夫王', './image/漁夫王.jpeg', '陣営：第３陣営\n漁夫王はクエストが3回成功時に暗殺される人を予想して選択します。\n選択した人が暗殺された場合、勝利した陣営と一緒に勝利します。\n※ローカル拡張役職です。'],
[32, 'タークィン', './image/モードレッドの手下３.jpeg', '陣営：第３陣営\nタークィンは役職に関係なく赤陣営全員を知っています。\nクエストを失敗に導き、3回目の失敗時に選出されていた場合、単独勝利します。\n※ローカル拡張役職です。'],
[33, '聖ミカエル山の巨人', './image/聖ミカエル山の巨人.jpeg', '陣営：第３陣営\n聖ミカエル山の巨人は役職に関係なく赤陣営全員を知っています。\nクエストに一度も選ばれずに終了した場合、または参加したクエストで累計３枚以上の失敗を出されることで単独勝利します。\n※ローカル拡張役職です。']
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
        [3,1],[4,1],[4,1],[5,2],[5,1]
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
.?:現在の状態
.h:コマンド一覧
.l:隠しコメントを表示(プレイ終了後)
.m:作成
"""
# ゲーム開始待ち : start -> ゲーム開始
usage_avalon1="""
.?:現在の状態
.h:コマンド一覧
.in:入室
.d 人数:デッキリスト
.ds 番号:デッキセット
.role:役職一覧
.role 番号:役職説明
.role プレイ人数分の数字:役職カスタマイズ
.s:開始
.stop:停止
"""
usage_avalon20="""
.?:現在の状態
.h:コマンド一覧
.s 数字:選出
.l:クエスト履歴(選出情報＋クエ結果)
.lq:クエスト結果履歴(クエ結果)
.role:役職一覧
.role 番号:役職説明
.stop:ゲーム停止
"""
usage_avalon21="""
.?:現在の状態
.h:コマンド一覧
.a:承認
.r:却下
.l:クエスト履歴(選出情報＋クエ結果)
.lq:クエスト結果履歴(クエ結果)
.role:役職一覧
.role 番号:役職説明
.stop:ゲーム停止
"""
usage_avalon22="""
.?:現在の状態
.h:コマンド一覧
.s:成功
.f/fail:失敗
.l:クエスト履歴(選出情報＋クエ結果)
.lq:クエスト結果履歴(クエ結果)
.role:役職一覧
.role 番号:役職説明
.stop:ゲーム停止
"""
usage_avalon23="""
.?:現在の状態
.h:コマンド一覧
.s:選択
.l:クエスト履歴(選出情報＋クエ結果)
.lq:クエスト結果履歴(クエ結果)
.role:役職一覧
.role 番号:役職説明
.stop:ゲーム停止
"""
usage_avalon24="""
.?:現在の状態
.h:コマンド一覧
.s 番号:調査
.l:クエスト履歴(選出情報＋クエ結果)
.lq:クエスト結果履歴(クエ結果)
.role:役職一覧
.role 番号:役職説明
.stop:ゲーム停止
"""
usage_avalon25="""
.?:現在の状態
.h:コマンド一覧
.s 番号:選択
.l:クエスト履歴(選出情報＋クエ結果)
.lq:クエスト結果履歴(クエ結果)
.role:役職一覧
.role 番号:役職説明
.stop:ゲーム停止
"""
usage_avalon26="""
.?:現在の状態
.h:コマンド一覧
.s 番号:選択
.l:クエスト履歴(選出情報＋クエ結果)
.lq:クエスト結果履歴(クエ結果)
.role:役職一覧
.role 番号:役職説明
.stop:ゲーム停止
"""
usage_avalon3="""
.?:現在の状態
.h:コマンド一覧
.k 数字:暗殺
.l:クエスト履歴(選出情報＋クエ結果)
.lq:クエスト結果履歴(クエ結果)
.role:役職一覧
.role 番号:役職説明
.stop:ゲーム停止
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

    if ary[0][4] != None:
        sql = f"{sql}[{ary[0][4]}]"

    for i in range(member_num):
        if i == 0: continue
        elif i == select_member:
            sql = f"{sql}\n■ {i+1}:{ary[i][1]}"
        else:
            sql = f"{sql}\n□ {i+1}:{ary[i][1]}"
        if ary[i][4] != None:
            sql = f"{sql}[{ary[i][4]}]"

    return sql

def role_find(member_num, ary, select_role_number):
    for i in range(member_num):
        if select_role_number == ary[i][3]:
            return i
    return None

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

    print("Logged in as " + client.user.name)

@client.event
async def on_message(ctx):
    # print("イベントを受け付けました。")
    # print(ctx.content)
    # print(ctx.channel.id)
    # if ctx.content == '???':
    #     print(datetime.now().strftime('%H:%M'))
    #     print(datetime.now().strftime('%w'))
    if ctx.author != client.user:
        comment = ctx.content
        if comment[0] == '.':
            try :
                # コネクションが切れた時に再接続してくれるよう設定
                cnt.ping(reconnect=True)
            except :
                print(f"再起動しました")
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

            # status : 状態表示
            if comment == '.?':
                if game_status == 0:
                    sql = f"部屋作成待ち状態です。\nゲームを始めるには部屋を作成してください。\nコマンド：m/make/作成"
                    embed = discord.Embed(title=f"現在の状況",description=sql)
                    await ctx.channel.send(embed=embed)
                elif game_status == 1:
                    dbsql = 'select * from `avalon_user`'
                    db.execute(dbsql)
                    rows = db.fetchall()
                    if game_member_num < 5:
                        sql = f"ゲーム開始準備の状態です。\
    \n現在の入室は{game_member_num}人です。\
    \n{player_display(game_member_num, rows, game_member_num+1)}\
    \n５人以上の入室(.in)と役職(.d,.ds,.role)を選択して、\
    \n開始コマンド(.s)を実行してください。"
                    else:
                        sql = f"ゲーム開始準備の状態です。\
    \n現在の入室は{game_member_num}人です。\
    \n{player_display(game_member_num, rows, game_member_num+1)}\
    \n役職(.d,.ds,.role)を選択して、\
    \n開始コマンド(.s)を実行することが可能です。"
                    embed = discord.Embed(title=f"現在の状況",description=sql)
                    await ctx.channel.send(embed=embed)
                elif game_status == 2:
                    dbsql = 'select * from `avalon_user`'
                    db.execute(dbsql)
                    rows = db.fetchall()
                    avalon_user = rows
                    print(avalon_user)
                    if game_phase != 5:
                        sql = "クエスト情報："
                        for i in range(5):
                            if i+1 == quest_cnt:
                                sql = f"{sql}\n■{i+1}クエ：{quest_member_num[game_member_num][i][0]}人"
                            else:
                                sql = f"{sql}\n□{i+1}クエ：{quest_member_num[game_member_num][i][0]}人"
                    else:
                        sql = "現在の状況："
                    if quest_cnt >= 2 or game_phase >= 1:
                        fdbsql = f"select * from `avalon_quest` where id = {int((quest_cnt-1)*5+vote_cnt)}"
                        db.execute(dbsql)
                        rows = db.fetchall()
                        avalon_quest = rows
                        print(avalon_quest)
                    if game_phase == 0:
                        sql = f"{sql}\n成功{quest_success_cnt}\n失敗{quest_fail_cnt}\nリーダは{avalon_user[select_member][1]}です。\n{player_display(game_member_num, avalon_user, select_member)}"
                        embed = discord.Embed(title=f"第{quest_cnt}クエスト：{vote_cnt}回目の選出:",description=f"リーダは{avalon_user[select_member][1]}です。\n{sql}")
                        await ctx.channel.send(embed=embed)
                        msg = client.get_user(avalon_user[select_member][2])
                        sql = f"あなたはリーダです。\n{quest_member_num[game_member_num][quest_cnt-1][0]}人選出してください\n1番〜3番の3人の選出例：.s 1,2,3\n{player_display(game_member_num, avalon_user, select_member)}"
                        embed = discord.Embed(title=f"第{quest_cnt}クエスト：{vote_cnt}回目の選出:",description=sql)
                        await msg.send(embed=embed)
                    elif game_phase == 1:
                        sql = f"{sql}\n成功{quest_success_cnt}\n失敗{quest_fail_cnt}"
                        sql = f"{sql}\n選出メンバー："
                        for i in range(quest_member_num[game_member_num][quest_cnt-1][0]):
                            sql = f"{sql}\n{game_member[i]+1}：{avalon_user[game_member[i]][1]}"

                        embed = discord.Embed(title=f"第{quest_cnt}クエスト：{vote_cnt}回目の承認却下:",description=f"{sql}")
                        await ctx.channel.send(embed=embed)

                        for i in range(game_member_num):
                            if avalon_quest[i] < 2:
                                msg = client.get_user(avalon_user[i][2])
                                embed = discord.Embed(title="クエストメンバー承認却下中",description=f"{sql}\n承認の場合 : a\n却下の場合 : .r\nを入力してください")
                                await msg.send(embed=embed)

                    elif game_phase == 2:
                        sql = f"{sql}\n現在の状況：\n成功{quest_success_cnt}\n失敗{quest_fail_cnt}\nリーダは{avalon_user[select_member][1]}です。\n選出者の成功失敗選択中です"
                        embed = discord.Embed(title=f"第{quest_cnt}クエスト：{vote_cnt}回目の成功失敗:",description=sql)
                        await ctx.channel.send(embed=embed)
                        sql = "選出メンバー"
                        for i in range(quest_member_num[game_member_num][quest_cnt-1][0]):
                            sql = f"{sql}\n{game_member[i]+1}：{avalon_user[game_member[i]][1]}"

                        for i in range(quest_member_num[game_member_num][quest_cnt-1][0]):
                            print(game_member[i])
                            print(avalon_quest)
                            print(avalon_quest[game_member[i]+1])
                            if avalon_quest[game_member[i]+1][3] < 8:
                                msg = client.get_user(avalon_user[game_member[i]][2])
                                embed = discord.Embed(title="クエスト中",description=f"{sql}\n成功の場合 : .s\n失敗の場合 : .f\nを入力してください")
                                await msg.send(embed=embed)
                    elif game_phase == 3:
                        sql = f"{sql}\n{quest_cnt-1}の乙女選択中です。\n{player_display(game_member_num, avalon_user, game_member_num+1)}"
                        embed = discord.Embed(title=f"第{quest_cnt}クエスト：{vote_cnt}回目の選出:",description=sql)
                    elif game_phase == 4:
                        sql = f"{sql}\n{player_display(game_member_num, avalon_user, game_member_num+1)}"
                        embed = discord.Embed(title=f"第{quest_cnt}クエスト：{vote_cnt}回目の乙女選出中:",description=sql)
                        await ctx.channel.send(embed=embed)
                        otome_select = [game_otome1, game_otome2, game_otome3]
                        otome_member = otome_select[quest_cnt-2]
                        msg = client.get_user(avalon_user[otome_member][2])
                        sql = player_display(game_member_num, avalon_user, select_member)
                        embed = discord.Embed(title=f"第{quest_cnt}クエスト：{vote_cnt}回目の乙女選出中:",description=f"現在の状況：\n成功{quest_success_cnt}\n失敗{quest_fail_cnt}\n{sql}\nあなたは乙女選出者です。\n選出例:1番のプレイヤーを暗殺する場合\n.s 1")
                        await msg.send(embed=embed)
                    # ビーストフェーズ：オベロン化するプレイヤー選択
                    elif game_phase == 5:
                        sql = f"{sql}\n{player_display(game_member_num, avalon_user, game_member_num+1)}"
                        embed = discord.Embed(title=f"{avalon_role[16][1]}の能力使用フェーズ",description=f"{sql}\nオベロンにするプレイヤーを選択中です。")
                        await ctx.channel.send(embed=embed)
                        beast_num = role_find(game_member_num, avalon_user, 16)
                        msg = client.get_user(avalon_user[beast_num][2])
                        sql = player_display(game_member_num, avalon_user, select_member)
                        embed = discord.Embed(title=f"{avalon_role[16][1]}の能力使用フェーズ",description=f"{sql}\nあなたは{avalon_role[16][1]}です。オベロンにするプレイヤーを選出してください。\n選出例:1番のプレイヤーをオベロンにしたい場合\n.s 1")
                        await msg.send(embed=embed)
                    # 漁夫フェーズ：暗殺予想
                    elif game_phase == 6:
                        n8_cnt = 0
                        if role_find(game_member_num, avalon_user, 8) != None:
                            for i in range(game_member_num):
                                if avalon_user[i][3] == 8:
                                    n8_cnt += 1

                        ex_member = role_find(game_member_num, avalon_user, 31)
                        msg = client.get_user(avalon_user[ex_member][2])
                        sql = "暗殺される人を予想してください"
                        if n8_cnt == 2:
                            sql = f"{sql}\nマーリンまたは{avalon_role[8][1]}の2人の一方を予想してください"
                            sql = f"{sql}\n{player_display(game_member_num, avalon_user, game_member_num+1)}\nマーリンを暗殺するコマンド例：\n１番のプレイヤーを暗殺すると予想する場合 : .s 1\n{avalon_role[8][1]}を暗殺するコマンド例：\n１番と２番のプレイヤーを暗殺すると予想する場合 : .s 1,2"
                        else:
                            sql = "{sql}\nマーリンを予想してください"
                            sql = f"{sql}\n{player_display(game_member_num, avalon_user, game_member_num+1)}\nコマンド例：１番のプレイヤーを暗殺する場合\n.k 1"
                        embed = discord.Embed()
                        embed.add_field(name=f"暗殺者の予想フェーズ", value=f"{sql}")
                        await msg.send(embed=embed)
                        embed = discord.Embed()
                        embed.add_field(name=f"暗殺者の予想フェーズ", value=f"{avalon_role[31][1]}が暗殺されるプレイヤーを予想中です")
                        await ctx.channel.send(embed=embed)

                elif game_status == 3:
                    n8_cnt = 0
                    if role_find(game_member_num, avalon_user, 8) != None:
                        for i in range(game_member_num):
                            if avalon_user[i][3] == 8:
                                n8_cnt += 1
                    kill_member = role_find(game_member_num, avalon_user, 12)
                    if kill_member == None:
                        kill_member = role_find(game_member_num, avalon_user, 16)
                    if kill_member == None:
                        kill_member = role_find(game_member_num, avalon_user, 11)
                    if kill_member == None:
                        kill_member = role_find(game_member_num, avalon_user, 10)
                    sql = f"{avalon_user[kill_member][1]}が暗殺中です。"
                    embed = discord.Embed(title=f"暗殺フェーズ",description=f"{sql}\n")
                    await ctx.channel.send(embed=embed)
                    msg = client.get_user(avalon_user[kill_member][2])
                    if n8_cnt == 2:
                        sql = f"マーリンまたは{avalon_role[8][1]}の2人の一方を予想して暗殺してください"
                        sql = f"{sql}\n{player_display(game_member_num, avalon_user, game_member_num+1)}\nマーリンを暗殺するコマンド例：\n１番のプレイヤーを暗殺する場合 : .k 1\n{avalon_role[8][1]}を暗殺するコマンド例：\n１番と２番のプレイヤーを暗殺する場合 : .k 1,2"
                    else:
                        sql = "マーリンを予想して暗殺してください"
                        sql = f"{sql}\n{player_display(game_member_num, avalon_user, game_member_num+1)}\nコマンド例：１番のプレイヤーを暗殺する場合\n.k 1"
                    embed = discord.Embed(title=f"暗殺フェーズ",description=f"{sql}\n")
                    await msg.send(embed=embed)

            # init : 初期化
            elif comment == '.init':
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
                sql = 'drop table if exists avalon_user'
                db.execute(sql)
                # テーブル作成
                sql = "create table if not exists `avalon_user` ( \
                `id` int, \
                `name` varchar(255), \
                `user_id` bigint, \
                `role` int, \
                `coming_out` varchar(20), \
                primary key (`id`) \
                )"
                db.execute(sql)
                await ctx.channel.send(f"データを初期化しました。")

            # help : ヘルプ
            elif comment == '.h':
                if game_status == 0:
                    embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon0)
                elif game_status == 1:
                    embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon1)
                elif game_status == 2:
                    if game_phase == 0:
                        embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon20)
                        # sql = 'select * from `avalon_user`'
                        # db.execute(sql)
                        # rows = db.fetchall()
                        # print(rows)
                    elif game_phase == 1:
                        embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon21)
                    elif game_phase == 2:
                        embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon22)
                    elif game_phase == 3:
                        embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon23)
                    elif game_phase == 4:
                        embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon24)
                    elif game_phase == 5:
                        embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon25)
                    elif game_phase == 6:
                        embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon25)
                elif game_status == 3:
                    embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon3)
                await ctx.channel.send(embed=embed)

            # instruction : 説明書
            elif comment == '.i':
                # print(glob.glob("./image/アヴァロン_説明書*"))
                file=glob.glob("./image/アヴァロン_説明書*")
                await ctx.channel.send("説明書を表示します", file=File(file[0]))
                await ctx.channel.send(file=File(file[1]))

            elif comment == '.l':
                if game_status == 0:
                    sql = 'select * from `avalon_comment`'
                    db.execute(sql)
                    rows = db.fetchall()
                    flg = 0
                    for i in rows:
                        if i[0] == None:
                            break
                        if flg == 0:
                            sql = f"{i[1]}"
                            flg = 1
                        else:
                            if i[0] == 'bot':
                                sql = f"{sql}\n{i[1]}"
                            else:
                                sql = f"{sql}\n{i[0]}：{i[1]}"

                    embed = discord.Embed(title="隠しコメント",description=sql)
                    await ctx.channel.send(embed=embed)

                elif game_status >= 2:
                    dbsql = 'select * from `avalon_user`'
                    db.execute(dbsql)
                    rows = db.fetchall()
                    avalon_user = rows
                    sql = 'select * from `avalon_quest`'
                    db.execute(sql)
                    rows = db.fetchall()
                    # print(len(rows))

                    game_info = [
                        [None,None,None,None],[None,None,None,None],[None,None,None,None],[None,None,None,None],[None,None,None,None],
                        [None,None,None,None],[None,None,None,None],[None,None,None,None],[None,None,None,None],[None,None,None,None],
                        [None,None,None,None],[None,None,None,None],[None,None,None,None],[None,None,None,None],[None,None,None,None],
                        [None,None,None,None],[None,None,None,None],[None,None,None,None],[None,None,None,None],[None,None,None,None],
                        [None,None,None,None],[None,None,None,None],[None,None,None,None],[None,None,None,None],[None,None,None,None]
                    ]
                    i = 0
                    for num in rows:
                        # print(num)
                        s_cnt = 0
                        f_cnt = 0
                        a_cnt = 0
                        if num[0] == None:
                            break
                        for k in range(game_member_num):
                            if int(num[1+k]) >= 16:
                                s_cnt += 1
                            elif int(num[1+k]) > 8:
                                f_cnt += 1
                            if int(num[1+k])%8 >= 2:
                                a_cnt += 1
                        if a_cnt >= game_member_num:
                            game_info[i][1] = s_cnt
                            game_info[i][2] = f_cnt
                            game_info[i][3] = 1
                        else:
                            game_info[i][3] = 0
                        if f_cnt == 0 and s_cnt == 0:
                            game_info[i][0] = 0
                        elif f_cnt >= quest_member_num[game_member_num][i][1]:
                            game_info[i][0] = 1
                        else:
                            game_info[i][0] = 2

                        i += 1

                    # print(game_info)
                    i = 0
                    flg = 0
                    for num in rows:
                        if num[0] == None:
                            break
                        q_num = int(int(num[0]-1)/5)+1
                        v_num = (int(num[0]-1)%5)+1
                        if game_info[i][3] == 1:
                            if i == 0:
                                sql = f"{q_num}クエ、{v_num}回目 : "
                            else:
                                sql = f"{sql}\n{q_num}クエ、{v_num}回目 : "
                        if game_info[i][1]+game_info[i][2] == quest_member_num[game_member_num][i][0]:
                            if game_info[i][0] == 2:
                                sql = f"{sql}成功：成功{game_info[i][1]},失敗{game_info[i][2]}"
                            elif game_info[i][0] == 1:
                                sql = f"{sql}失敗：成功{game_info[i][1]},失敗{game_info[i][2]}"
                        for k in range(game_member_num):
                            if int(num[1+k]) >= 16:
                                s_cnt += 1
                            else:
                                f_cnt += 1
                            if game_info[i][3] == 1:
                                flg = 1
                                if int(num[1+k])%2 == 1:
                                    if int(num[1+k])%8 >= 4:
                                        sql = f"{sql}\n■{k+1} : {avalon_user[k][1]}：承認"
                                    else:
                                        sql = f"{sql}\n■{k+1} : {avalon_user[k][1]}：却下"
                                else:
                                    if int(num[1+k])%8 >= 4:
                                        sql = f"{sql}\n□{k+1} : {avalon_user[k][1]}：承認"
                                    else:
                                        sql = f"{sql}\n□{k+1} : {avalon_user[k][1]}：却下"

                        i += 1

                    if flg == 0:
                        sql = 'まだ1回も選出されていません。'
                    embed = discord.Embed(title="クエスト履歴",description=sql)
                    await ctx.channel.send(embed=embed)
                else:
                    await ctx.channel.send(f"このコマンドは無効です。：{comment}")

            elif comment == '.lq':
                if game_status >= 2:
                    dbsql = 'select * from `avalon_user`'
                    db.execute(dbsql)
                    rows = db.fetchall()
                    avalon_user = rows
                    sql = 'select * from `avalon_quest`'
                    db.execute(sql)
                    rows = db.fetchall()
                    # print(len(rows))

                    game_info = [
                        [None,None,None,None],[None,None,None,None],[None,None,None,None],[None,None,None,None],[None,None,None,None],
                        [None,None,None,None],[None,None,None,None],[None,None,None,None],[None,None,None,None],[None,None,None,None],
                        [None,None,None,None],[None,None,None,None],[None,None,None,None],[None,None,None,None],[None,None,None,None],
                        [None,None,None,None],[None,None,None,None],[None,None,None,None],[None,None,None,None],[None,None,None,None],
                        [None,None,None,None],[None,None,None,None],[None,None,None,None],[None,None,None,None],[None,None,None,None]
                    ]
                    i = 0
                    for num in rows:
                        # print(num)
                        s_cnt = 0
                        f_cnt = 0
                        a_cnt = 0
                        if num[0] == None or num[1] == None or num[2] == None:
                            break
                        for k in range(game_member_num):
                            if int(num[1+k]) >= 16:
                                s_cnt += 1
                            elif int(num[1+k]) > 8:
                                f_cnt += 1
                            if int(num[1+k])%8 >= 2:
                                a_cnt += 1
                        if a_cnt >= game_member_num:
                            game_info[i][1] = s_cnt
                            game_info[i][2] = f_cnt
                            game_info[i][3] = 1
                        else:
                            game_info[i][3] = 0
                        if f_cnt == 0 and s_cnt == 0:
                            game_info[i][0] = 0
                        elif f_cnt >= quest_member_num[game_member_num][i][1]:
                            game_info[i][0] = 1
                        else:
                            game_info[i][0] = 2

                        i += 1

                    # print(game_info)
                    flg = 0
                    i = 0
                    k = 0
                    # print(game_info)
                    for num in rows:
                        # print(num)
                        if num[0] == None or num[1] == None or num[2] == None:
                            break
                        if game_info[i][0] != 0:
                            flg = 1
                        q_num = int(int(num[0])/5)+1
                        v_num = int(num[0])%game_member_num
                        if k == 0:
                            sql = f"{q_num}クエ: "
                        else:
                            sql = f"{sql}\n{q_num}クエ: "
                        if game_info[i][1]+game_info[i][2] == quest_member_num[game_member_num][i][0]:
                            if game_info[i][0] == 2:
                                sql = f"{sql}成功：成功{game_info[i][1]},失敗{game_info[i][2]}"
                            elif game_info[i][0] == 1:
                                sql = f"{sql}失敗：成功{game_info[i][1]},失敗{game_info[i][2]}"
                        sql = f"{sql}\n"
                        sql_member = f"メンバー："
                        for k in range(game_member_num):
                            if int(num[1+k])%2 == 1:
                                sql_member = f"{sql_member}[{k+1}]{avalon_user[k][1]}"
                        sql = f"{sql}{sql_member}"
                        i += 1
                        k += 1

                    if flg == 0:
                        sql = 'まだ1回もクエストへ行っていません'
                    embed = discord.Embed(title="クエスト履歴",description=sql)
                    await ctx.channel.send(embed=embed)
                else:
                    await ctx.channel.send(f"このコマンドは無効です。：{comment}")

            elif game_status == 0:
                # make : 部屋作成
                if comment == '.m':
                    if game_status == 0:
                        sql = 'drop table if exists avalon_data'
                        db.execute(sql)
                        sql = 'drop table if exists avalon_user'
                        db.execute(sql)
                        sql = 'drop table if exists avalon_quest'
                        db.execute(sql)
                        sql = 'drop table if exists avalon_comment'
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
                        sql = "create table if not exists `avalon_comment` ( \
                        `user` varchar(20), \
                        `comment` varchar(255) \
                        )"
                        db.execute(sql)
                        sql = "create table if not exists `avalon_data` ( \
                        `id` int, \
                        `channel_id` bigint, \
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

                        sql = f"insert into `avalon_comment` (`user`, `comment`) \
                        value (%s, %s)"
                        value = ('bot', 'ゲームが開始しました。')
                        db.execute(sql, value)
                        # テーブル作成 ユーザ情報
                        sql = "create table if not exists `avalon_user` ( \
                        `id` int, \
                        `name` varchar(255), \
                        `user_id` bigint, \
                        `role` int, \
                        `coming_out` varchar(20), \
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
                        await ctx.channel.send(f"{ctx.author.display_name}が部屋を作成し、入室しました。\n現在１人です。\n５人以上集まればゲームを開始できます。")
                        embed = discord.Embed(title="現在使用可能なコマンド一覧",description=usage_avalon1)
                        await ctx.channel.send(embed=embed)
                    else :
                        await ctx.channel.send(f"このコマンドは無効です。：{comment}")
                else:
                    await ctx.channel.send(f"このコマンドは無効です。：{comment}")
            elif game_status == 1:
                msgch = client.get_channel(channel_id)
                # login : 部屋入室
                if comment == '.in':
                    if game_member_num < 10:
                        gm_num = game_member_num + 1
                        if gm_num < 5:
                            await msgch.send(f"{gm_num}人目:{ctx.author.display_name}が入室しました。")
                        else:
                            await msgch.send(f"{gm_num}人目:{ctx.author.display_name}が入室しました。\n5人以上入室したため、開始コマンド(.s)でゲームを開始することができます。")
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
                        await ctx.channel.send(f"満室です。")

                # deck number: デッキリスト
                elif comment[0:3] == '.d ':
                    deck_cmd = comment.lstrip(".d ")
                    deck_num = int(deck_cmd)
                    if deck_num > 4 and deck_num < 11 :
                        role = role_list_display(deck_num)
                        for i in range(len(role)):
                            if i == 0:
                                embed = discord.Embed(title=f"役職{i+1}",description=role[i])
                            else:
                                embed.add_field(name=f"役職{i+1}",value=role[i])
                        await ctx.channel.send(embed=embed)
                    else:
                        await ctx.channel.send(f"ゲームは5人〜10人です。：{comment}")

                # deck set: デッキ設定
                elif comment[0:4] == '.ds ':
                    deck_cmd = comment.lstrip(".ds ")
                    game_role = int(deck_cmd)
                    if game_role > 0 and game_role <= len(avalon_role_auto[game_member_num]) :
                        sql = f"update `avalon_data` set `game_role`={game_role} where id = 0"
                        await msgch.send(f"デッキを{game_role}に設定しました。")
                    else:
                        await ctx.channel.send(f"このコマンドは無効です。：{comment}")
                        sql = f"update `avalon_data` set `game_role`=1 where id = 0"
                        await msgch.send(f"デッキを1に設定しました。")
                    db.execute(sql)

                # role number : 役職カスタマイズ
                elif comment == ".role":
                    for i in range(34):
                        if i == 0:
                            blue_role = f"{avalon_role[i][0]}:{avalon_role[i][1]}"
                        elif i < 9:
                            blue_role = f"{blue_role}\n{avalon_role[i][0]}:{avalon_role[i][1]}"
                        elif i == 10:
                            red_role = f"{avalon_role[i][0]}:{avalon_role[i][1]}"
                        elif i >= 11 and i <=16:
                            red_role = f"{red_role}\n{avalon_role[i][0]}:{avalon_role[i][1]}"
                        elif i == 20:
                            other_role = f"{avalon_role[i][0]}:{avalon_role[i][1]}"
                        elif (i >= 30 and i <=33) or i == 21:
                            other_role = f"{other_role}\n{avalon_role[i][0]}:{avalon_role[i][1]}"
                    embed = discord.Embed(title="",description="")
                    embed.add_field(name="青陣営",value=blue_role)
                    embed.add_field(name="赤陣営",value=red_role)
                    embed.add_field(name="その他",value=other_role)
                    embed.add_field(name="コマンド例",value="0:マーリン\n1:パーシヴァル\n3:情弱\n11:モルガナ\n12:暗殺者\nの場合\n.role 0,1,2,11,12\n入室人数に合わせて\n設定してください。")
                    await ctx.channel.send(embed=embed)

                # role number : 役職カスタマイズ
                elif comment[0:6] == '.role ':
                    deck_cmd_re = re.compile('\d+')
                    deck_cmd_match = deck_cmd_re.findall(comment)

                    if len(deck_cmd_match) == 1:
                        num = int(deck_cmd_match[0])
                        if (num >= 0 and num <=8) or (num >= 10 and num <=16) or (num >= 20 and num <= 21) or (num >= 30 and num <= 33):
                            for i in avalon_role:
                                if i[0] == num:
                                    embed = discord.Embed(title=f"役職説明:{i[1]}",description=i[3])
                                    if i[2] != None:
                                        file = i[2]
                                        await ctx.channel.send(embed=embed, file=File(file))
                                    else:
                                        await ctx.channel.send(embed=embed)
                        else:
                            await ctx.channel.send("指定番号の役職はありません")
                    elif len(deck_cmd_match) < 5:
                        await ctx.channel.send("プレイヤー数が5人に達していません。\n5人以上入室後、人数に合わせてコマンドしてください。")
                    elif len(deck_cmd_match) == game_member_num:
                        role_list = [0,1]
                        i = 0
                        for k in deck_cmd_match:
                            if (k != None):
                                if i < 2 :
                                    role_list[i] = int(k)
                                else :
                                    role_list.append(int(k))
                                i = i + 1

                        err_flg = 0
                        n8_ok = 1
                        n8_cnt = 0
                        for k in range(len(role_list)):
                            num = role_list[k]
                            if num == 8:
                                n8_cnt += 1
                            if (num >= 0 and num <=8) or (num >= 10 and num <=16) or (num >= 20 and num <= 21) or (num >= 30 and num <= 33):
                                continue
                            else:
                                err_flg = 1
                        if n8_cnt != 0 and n8_cnt != 2:
                            n8_ok = 0
                            err_flg = 1

                        if err_flg == 0:
                            for k in range(game_member_num):
                                sql = f"update `avalon_user` set `role`={role_list[k]} where id = {k+1}"
                                db.execute(sql)
                                if k == 0:
                                    sql_role = f"{avalon_role[role_list[k]][1]}"
                                else:
                                    sql_role = f"{sql_role}\n{avalon_role[role_list[k]][1]}"

                            sql = f"update `avalon_data` set `game_role`= 999 where id = 0"
                            db.execute(sql)
                            await msgch.send(f"デッキをカスタマイズしました。\nもし（未対応）の表示がある場合には、対応していないため変更してください。")
                            embed = discord.Embed(title="選択役職",description=sql_role)
                            await msgch.send(embed=embed)
                        else:
                            sql = f"update `avalon_data` set `game_role`= 1 where id = 0"
                            db.execute(sql)
                            if n8_ok == 0:
                                sql = f"{avalon_role[8][1]}を入れる場合、2人入れてください。不正があったため、デッキを1にセットしました。"
                            else:
                                sql = f"セットした数値に使用できない数値がありました。\nデッキを1にセットしました"
                            for i in range(game_member_num):
                                sql = f"{sql}\n{avalon_role[avalon_role_auto[game_member_num][0][i]][1]}"
                            embed = discord.Embed(title="選択役職",description=sql)
                            await msgch.send(embed=embed)
                    elif len(deck_cmd_match) < game_member_num:
                        await ctx.channel.send("プレイヤー数より役職の指定数が少ないです。\n合わせたコマンドにしてください。")
                    else:
                        await ctx.channel.send("プレイヤー数と役職の指定数が違います。\n合わせたコマンドにしてください。")

                # otome : 乙女設定
                elif comment == '.o':
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
                elif comment == '.e':
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
                elif comment == '.s':
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
                        ary = [[1,'name1', 1, 1, '1'], [2, 'name2', 2, 2, '2']]
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
                            ary.append([rows[0], rows[1], rows[2], rows[3], rows[4]])
                            user_id[i] = rows[2]
                            # print(rows[3])
                            role[i] = rows[3]

                        ary.pop(0)
                        ary.pop(0)

                        # print(role)
                        for i in range(game_member_num) :
                            if game_role != 999:
                                role[i] = avalon_role_auto[game_member_num][game_role-1][i]

                        random.shuffle(role)
                        for i in range(game_member_num) :
                            ary[i][3] = role[i]
                        random.shuffle(ary)
                        beast = 0
                        for i in range(game_member_num) :
                            num = i + 1
                            sql = f"update `avalon_user` set \
                            `name` = '{ary[i][1]}',\
                            `user_id` = {ary[i][2]},\
                            `role` = {ary[i][3]} \
                            where id = {i+1}"
                            # print(sql)
                            db.execute(sql)

                        if role_find(game_member_num, ary, 16) == None:
                            for i in range(game_member_num):
                                msg = client.get_user(ary[i][2])
                                if avalon_role[i][3] == 6 or avalon_role[i][3] == 30:
                                    await msg.send(f"あなたの役職は{avalon_role[ary[i][3]][1]}です。")
                                else:
                                    await msg.send(f"あなたの役職は{avalon_role[ary[i][3]][1]}です。", file=File(avalon_role[ary[i][3]][2]))
                                if ary[i][3] == 0 : # マーリン
                                    role_info = '赤陣営は\n'
                                    flg = 0
                                    for j in range(game_member_num):
                                        if ((ary[j][3] >= 11 and ary[j][3] <= 16) or ary[j][3] == 6) and ary[j][3] != 15:
                                            role_info = f"{role_info}\n{j+1}：{ary[j][1]}"
                                            if ary[j][3] == 6:
                                                flg = 1
                                    role_info = f"{role_info}\nです。\nバレないようにクエスト勝利へ導いてください。"
                                    if flg == 1:
                                        role_info = f"{role_info}\nカラドックは赤陣営として通知されます。※ローカル拡張役職です。"
                                    await msg.send(f"{role_info}")
                                elif ary[i][3] == 1 : # パーシヴァル
                                    role_info = 'マーリンとモルガナを確認することができます。\n'
                                    for j in range(game_member_num):
                                        if ary[j][3] == 0 or ary[j][3] == 11:
                                            role_info = f"{role_info}\n{j+1}：{ary[j][1]}"
                                    role_info = f"{role_info}\nがマーリンとモルガナです。\n役職によって2人とは限りません。"
                                    await msg.send(f"{role_info}")
                                elif ary[i][3] == 2 : # ガラハッド
                                    role_info = f"パーシヴァルと暗殺者と{avalon_role[16][1]}を確認することができます。\n"
                                    for j in range(game_member_num):
                                        if (ary[j][3] == 1 or ary[j][3] == 12 or ary[j][3] == 16):
                                            role_info = f"{role_info}\n{j+1}：{ary[j][1]}"
                                    role_info = f"{role_info}\n役職によって3人とは限りません。"
                                    await msg.send(f"{role_info}")
                                elif ary[i][3] == 6 : # カラドック
                                    role_info = f"青陣営ですが、マーリンに赤として通知されます。\n※ローカル拡張役職です。"
                                    await msg.send(f"{role_info}")
                                elif ary[i][3] == 8 : # 恋人
                                    role_info = "恋人同士は"
                                    for j in range(game_member_num):
                                        if ary[j][3] == 8:
                                            role_info = f"{role_info}\n{j+1}：{ary[j][1]}"
                                    role_info = f"{role_info}\nです。\n暗殺者に恋人同士の2人が暗殺されてしまうと、負けてしまいます。\nバレないようにプレイしてください。\n※ローカル拡張役職です。"
                                    await msg.send(f"{role_info}")
                                elif (ary[i][3] >= 10 and ary[i][3] <= 19) and ary[i][3] != 14 and ary[i][3] != 15: # 赤陣営
                                    role_info = '赤陣営は\n'
                                    for j in range(game_member_num):
                                        if (ary[j][3] >= 10 and ary[j][3] <= 19) and ary[j][3] != 14 and ary[j][3] != 15:
                                            role_info = f"{role_info}\n{j+1}：{ary[j][1]}"
                                    role_info = f"{role_info}\nです。"
                                    if role_find(game_member_num, ary, 14) != None:
                                        if role_find(game_member_num, ary, 15) != None:
                                            role_info = f"{role_info}\nただし{avalon_role[14][1]}と{avalon_role[15][1]}は見えません。"
                                        else:
                                            role_info = f"{role_info}\nただし{avalon_role[14][1]}は見えません。"
                                    else:
                                        if role_find(game_member_num, ary, 15) != None:
                                            role_info = f"{role_info}\nただし{avalon_role[15][1]}は見えません。"
                                    await msg.send(f"{role_info}")
                                elif ary[i][3] == 14: # 赤陣営
                                    role_info = f"あなたは仲間の赤陣営を知りません。"
                                    if role_find(game_member_num, ary, 15) != None:
                                        role_info = f"{role_info}\n{avalon_role[15][1]}を除いて赤陣営はあなたを知りません。"
                                    else:
                                        role_info = f"{role_info}\n赤陣営はあなたを知りません。"
                                    await msg.send(f"{role_info}")
                                elif ary[i][3] == 15: # 赤陣営
                                    role_info = '赤陣営は\n'
                                    for j in range(game_member_num):
                                        if ary[j][3] >= 10 and ary[j][3] <= 19:
                                            role_info = f"{role_info}\n{j+1}：{ary[j][1]}"
                                    role_info = f"{role_info}\nです。\n他の赤陣営にはあなたは知らされていません。"
                                    await msg.send(f"{role_info}")
                                elif ary[i][3] >= 30 and ary[i][3] <= 33: # 赤陣営
                                    if ary[i][3] == 31:
                                        role_info = f"あなたは情報を知りません。\n勝利条件は暗殺フェーズ直前に暗殺されるプレイヤーを予想し、当てることです"
                                    else:
                                        role_info = '赤陣営は\n'
                                        for j in range(game_member_num):
                                            if (ary[j][3] >= 10 and ary[j][3] < 20):
                                                role_info = f"{role_info}\n{j+1}：{ary[j][1]}"
                                        if ary[i][3] == 30:
                                            role_info = f"{role_info}\nです。\n勝利条件は暗殺されることです。"
                                        elif ary[i][3] == 32:
                                            role_info = f"{role_info}\nです。\n3回目の失敗でクエストに参加していると単独勝利します。\n{avalon_role[33][1]}の勝利条件と同時成立した場合、同時勝利です。"
                                        elif ary[i][3] == 33:
                                            role_info = f"{role_info}\nです。\n一度もクエストに選ばれない、または参加したクエストの失敗数の累計が3枚以上の場合、単独勝利します。\n{avalon_role[32][1]}の勝利条件と同時成立した場合、同時勝利です。"
                                    await msg.send(f"{role_info}")

                            role.sort()
                            sql = f"{game_member_num}人戦のクエスト："
                            for i in range(5):
                                sql = f"{sql}\n{i+1}クエ：{quest_member_num[game_member_num][i][0]}人"
                            embed = discord.Embed(title=f"ゲーム開始",description=sql)
                            sql = "役職："
                            for i in range(game_member_num):
                                sql = f"{sql}\n{avalon_role[role[i]][1]}"

                            embed.add_field(name=f"役職",value=sql)
                            sql = f"現在の状況：\n成功{quest_success_cnt}\n失敗{quest_fail_cnt}\nリーダは{ary[select_member][1]}です。\n{player_display(game_member_num, ary, select_member)}"
                            embed.add_field(name=f"第{quest_cnt}クエスト：{vote_cnt}回目の選出:",value=sql)
                            await msgch.send(embed=embed)
                            msg = client.get_user(ary[select_member][2])
                            sql = f"あなたはリーダです。\n{quest_member_num[game_member_num][quest_cnt-1][0]}人選出してください\n1番〜3番の3人の選出例：.s 1,2,3\n{player_display(game_member_num, ary, select_member)}"
                            embed = discord.Embed(title=f"第{quest_cnt}クエスト：{vote_cnt}回目の選出:",description=sql)
                            await msg.send(embed=embed)
                        else:
                            for i in range(game_member_num):
                                msg = client.get_user(ary[i][2])
                                if avalon_role[i][3] != 16:
                                    await msg.send(f"あなたの役職は{avalon_role[ary[i][3]][1]}です。", file=File(avalon_role[ary[i][3]][2]))
                                else:
                                    role_info = '赤陣営は\n'
                                    for j in range(game_member_num):
                                        if (ary[i][3] >= 10 and ary[i][3] <= 19) and ary[i][3] != 14:
                                            role_info = f"{role_info}\n{ary[j][1]}"
                                    role_info = f"{role_info}\nです。"
                                    await msg.send(f"あなたの役職は{avalon_role[ary[i][3]][1]}です。\n{role_info}", file=File(avalon_role[ary[i][3]][2]))
                            sql = player_display(game_member_num, ary, game_member_num+1)
                            embed = discord.Embed(title=f"{avalon_role[16][1]}能力フェーズ",description=f"{sql}\nオベロンにしたいプレイヤーを選択してください。\nコマンド例：１番のプレイヤーをオベロンにしたい場合\n.s 1")
                            beast_num = role_find(game_member_num, ary, 16)
                            msg = client.get_user(ary[beast_num][2])
                            await msg.send(embed=embed)
                            await msgch.send(f"{avalon_role[16][1]}がいるため、一時通知をしました。\nオベロン化するプレイヤーを選択後、最終通知を行います。\n{sql}")
                            game_phase = 5
                            sql = f"update `avalon_data` set `game_phase`={game_phase} where id = 0"
                            db.execute(sql)
                            sql = f"insert into `avalon_comment` (`user`, `comment`) \
                            value (%s, %s)"
                            value = ('bot', f"{avalon_role[16][1]}能力フェーズ")
                            db.execute(sql, value)

                        # テーブル作成
                        sql = "create table `avalon_quest` ( `id` int,"
                        for i in range(game_member_num):
                            sql = f"{sql} `member{i+1}` int,"
                        sql = f"{sql} primary key (`id`) )"
                        db.execute(sql)

                    else :
                        await ctx.channel.send(f"このコマンドは無効です。：{comment}\
                        \n現在の入室人数は{game_member_num}人です。\
                        \nあと{5-game_member_num}以上入室してからsコマンドを実行してください。")

                elif comment == '.stop':
                    await msgch.send("部屋を削除しました")
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
                    sql = 'drop table if exists avalon_user'
                    db.execute(sql)
                    # テーブル作成
                    sql = "create table if not exists `avalon_user` ( \
                    `id` int, \
                    `name` varchar(255), \
                    `user_id` bigint, \
                    `role` int, \
                    `comming_out` varchar(20), \
                    primary key (`id`) \
                    )"
                    db.execute(sql)
                else:
                    await ctx.channel.send(f"このコマンドは無効です。：{comment}")
            elif game_status == 2:
                msgch = client.get_channel(channel_id)
                quest_id = int((quest_cnt-1)*5+vote_cnt)
                avalon_user = [[1, 'name1', 1, 1, '1'], [1, 'name2', 2, 2, '2']]
                for i in range(game_member_num) :
                    sql = f"select * from `avalon_user` where id = {i+1}"
                    db.execute(sql)
                    rows = db.fetchone()
                    if rows[4] != None:
                        avalon_user.append([0, rows[1], rows[2], rows[3], rows[4]])
                    else:
                        avalon_user.append([0, rows[1], rows[2], rows[3], None])
                avalon_user.pop(0)
                avalon_user.pop(0)

                avalon_quest = [0]*game_member_num
                if game_phase != 0 and game_phase != 5:
                    sql = f"select * from `avalon_quest` where id = {int((quest_cnt-1)*5+vote_cnt)}"
                    db.execute(sql)
                    rows = db.fetchone()
                    for i in range(game_member_num):
                        avalon_quest[i] = int(rows[i+1])

                if comment[0:3] == '.n ':
                    cmd = comment.lstrip("n ")
                    sql = f"insert into `avalon_comment` (`user`, `comment`) \
                    value (%s, %s)"
                    value = (f"{ctx.author.display_name}", f"{cmd}")
                    db.execute(sql, value)
                    await ctx.author.send(f"コメントを受け付けました。")

                elif comment == '.stop':
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
                    sql = 'drop table if exists avalon_user'
                    db.execute(sql)
                    # テーブル作成
                    sql = "create table if not exists `avalon_user` ( \
                    `id` int, \
                    `name` varchar(255), \
                    `user_id` bigint, \
                    `role` int, \
                    `comming_out` varchar(20), \
                    primary key (`id`) \
                    )"
                    db.execute(sql)

                # role number : 役職カスタマイズ
                elif comment == '.role':
                    for i in range(34):
                        if i == 0:
                            blue_role = f"{avalon_role[i][0]}:{avalon_role[i][1]}"
                        elif i < 9:
                            blue_role = f"{blue_role}\n{avalon_role[i][0]}:{avalon_role[i][1]}"
                        elif i == 10:
                            red_role = f"{avalon_role[i][0]}:{avalon_role[i][1]}"
                        elif i >= 11 and i <=16:
                            red_role = f"{red_role}\n{avalon_role[i][0]}:{avalon_role[i][1]}"
                        elif i == 20:
                            other_role = f"{avalon_role[i][0]}:{avalon_role[i][1]}"
                        elif (i >= 30 and i <=33) or i == 21 or i == 22:
                            other_role = f"{other_role}\n{avalon_role[i][0]}:{avalon_role[i][1]}"
                    embed = discord.Embed(title="",description="")
                    embed.add_field(name="青陣営",value=blue_role)
                    embed.add_field(name="赤陣営",value=red_role)
                    embed.add_field(name="その他",value=other_role)
                    embed.add_field(name="コマンド例",value="0:マーリン\n1:パーシヴァル\n3:情弱\n11:モルガナ\n12:暗殺者\nの場合\nrole 0,1,2,11,12\n入室人数に合わせて\n設定してください。")
                    await ctx.channel.send(embed=embed)

                # role number : 役職カスタマイズ
                elif comment[0:6] == '.role ':
                    deck_cmd_re = re.compile('\d+')
                    deck_cmd_match = deck_cmd_re.findall(comment)

                    if len(deck_cmd_match) == 1:
                        num = int(deck_cmd_match[0])
                        if (num >= 0 and num <=8) or (num >= 10 and num <=16) or (num >= 20 and num <= 22) or (num >= 30 and num <= 33):
                            for i in avalon_role:
                                if i[0] == num:
                                    embed = discord.Embed(title=f"役職説明:{i[1]}",description=i[3])
                                    if i[2] != None:
                                        file = i[2]
                                        await ctx.channel.send(embed=embed, file=File(file))
                                    else:
                                        await ctx.channel.send(embed=embed)
                        else:
                            await ctx.channel.send("指定番号の役職はありません")

                elif comment[0:3] == '.c ' or comment == '.c':
                    if comment[0:3] == '.c ':
                        cmd = comment.lstrip(".c ")
                        if (len(cmd) != 0):
                            for i in range(game_member_num):
                                if ctx.author.id == avalon_user[i][2]:
                                    sql = f"update `avalon_user` set `coming_out` = '{cmd}' where id = {i+1}"
                                    db.execute(sql)
                                    await msgch.send(f"{avalon_user[i][1]}が{cmd}であると名乗り出ました。")
                                else:
                                    sql = f"update `avalon_user` set `coming_out` = NULL where id = {i+1}"
                                    db.execute(sql)
                                    await msgch.send(f"{avalon_user[i][1]}が{avalon_user[i][4]}であることを撤回しました。")
                    else:
                        for i in range(game_member_num):
                            if ctx.author.id == avalon_user[i][2]:
                                print(avalon_user[i][4])
                                if avalon_user[i][4] != None:
                                    sql = f"update `avalon_user` set `coming_out` = NULL where id = {i+1}"
                                    db.execute(sql)
                                    await msgch.send(f"{avalon_user[i][1]}が{avalon_user[i][4]}であることを撤回しました。")

                elif game_phase == 0: #選出フェーズ
                    # start game : ゲームを開始する
                    if comment[0:3] == '.s ':
                        if ctx.author.id == avalon_user[select_member][2]:
                            select_member_com = re.compile('\d+')
                            select_member_match = select_member_com.findall(comment)
                            # 重複チェック
                            if len(select_member_match) == len(set(select_member_match)):
                                if len(select_member_match) != quest_member_num[game_member_num][quest_cnt-1][0]:
                                    await ctx.channel.send(f"このコマンドは無効です。：{comment}\
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
                                                    select_list[i] = int(k)-1
                                                    avalon_quest[select_list[i]] = 1
                                                else :
                                                    select_list.append(int(k)-1)
                                                    avalon_quest[select_list[i]] = 1
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

                                        avalon_quest.insert(0, int((quest_cnt-1)*5+vote_cnt))
                                        db.execute(sql, avalon_quest)

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
                                                    user_name = f"{select_list[i]+1}:{avalon_user[select_list[i]][1]}"
                                                else:
                                                    user_name = f"{user_name}\n{select_list[i]+1}:{avalon_user[select_list[i]][1]}"

                                        if vote_cnt != 5:
                                            embed = discord.Embed(title="選出メンバー",description=f"{user_name}")
                                        else:
                                            embed = discord.Embed(title="選出メンバー",description=f"{user_name}\nこの選出が却下された場合、赤陣営の勝利です。")
                                        await msgch.send(embed=embed)
                                        for k in range(game_member_num):
                                            msg = client.get_user(avalon_user[k][2])
                                            if avalon_quest[k+1]%2 == 1:
                                                if vote_cnt != 5:
                                                    embed = discord.Embed(title="選出メンバー",description=f"{user_name}\nあなたは選出されています。\n承認 : .a\n却下 : .r\nを入力してください")
                                                    await msg.send(embed=embed)
                                                else:
                                                    embed = discord.Embed(title="選出メンバー",description=f"{user_name}\nあなたは選出されています。\n承認 : .a\n却下 : .r\nを入力してください\nこの選出が却下された場合、赤陣営の勝利です。")
                                                    await msg.send(embed=embed)
                                            else:
                                                if vote_cnt != 5:
                                                    embed = discord.Embed(title="選出メンバー",description=f"{user_name}\nあなたは選出されていません。\n承認 : .a\n却下 : .r\nを入力してください")
                                                    await msg.send(embed=embed)
                                                else:
                                                    embed = discord.Embed(title="選出メンバー",description=f"{user_name}\nあなたは選出されていません。\n承認 : .a\n却下 : .r\nを入力してください\nこの選出が却下された場合、赤陣営の勝利です。")
                                                    await msg.send(embed=embed)
                                        sql = f"insert into `avalon_comment` (`user`, `comment`) \
                                        value (%s, %s)"
                                        value = ('bot', f"{ctx.author.display_name}が{quest_cnt}クエの{vote_cnt}回目の選出")
                                        db.execute(sql, value)
                                    else:
                                        await ctx.channel.send(f"選出番号は1〜{game_member_num}から選んでください。：{comment}")
                            else:
                                await ctx.channel.send(f"重複しないメンバー選出をお願いします。：{comment}")
                        else:
                            await ctx.channel.send(f"あなたは選出リーダではありません。")
                    else:
                        await ctx.channel.send(f"このコマンドは無効です。：{comment}")

                elif game_phase == 1: #承認却下フェーズ
                    command_accept = 0
                    if comment == '.a' or comment == '.r':
                        if comment == '.a':
                            command_accept = 4
                        elif comment == '.r':
                            command_accept = 2

                        for i in range(game_member_num):
                            if ctx.author.id == avalon_user[i][2]:
                                msg = client.get_user(avalon_user[i][2])
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
                                        await msgch.send(f"{ctx.author.display_name}が上書きしました。")
                                    else:
                                        await msg.send(f"承認へ上書きしました。")
                                        await msgch.send(f"{ctx.author.display_name}が上書きしました。")
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

                                    sql = f"選出メンバー："
                                    for i in range(quest_member_num[game_member_num][quest_cnt-1][0]):
                                        sql = f"{sql}\n{game_member[i]+1}：{avalon_user[game_member[i]][1]}"
                                    embed = discord.Embed(title="投票結果",description=f"{vote_msg}\n{sql}\n選出メンバーが成功失敗の投票中です。")
                                    file = "./image/承認.jpeg"
                                    await msgch.send(embed=embed, file=File(file))

                                    for k in range(game_member_num):
                                        if avalon_quest[k]%2 == 1:
                                            msg = client.get_user(avalon_user[k][2])
                                            embed = discord.Embed(title="クエスト参加",description=f"{sql}\n成功の場合 : .s\n失敗の場合 : .f\nを入力してください")
                                            await msg.send(embed=embed)
                                    sql = f"insert into `avalon_comment` (`user`, `comment`) \
                                    value (%s, %s)"
                                    value = ('bot', f"{quest_cnt}クエ、{vote_cnt}回目承認\n")
                                    db.execute(sql, value)
                                    sql = "クエスト情報："
                                    for i in range(5):
                                        if i+1 == quest_cnt:
                                            sql = f"{sql}\n■{i+1}クエ：{quest_member_num[game_member_num][i][0]}人"
                                        else:
                                            sql = f"{sql}\n□{i+1}クエ：{quest_member_num[game_member_num][i][0]}人"
                                    sql = f"{sql}\n成功{quest_success_cnt}\n失敗{quest_fail_cnt}"
                                    sql = f"{sql}\n選出メンバー："
                                    for i in range(quest_member_num[game_member_num][quest_cnt-1][0]):
                                        sql = f"{sql}\n{game_member[i]+1}：{avalon_user[game_member[i]][1]}"

                                    for i in range(game_member_num):
                                        if avalon_quest[i]%2 == 1:
                                            msg = client.get_user(avalon_user[i][2])
                                            embed = discord.Embed(title=f"第{quest_cnt}クエスト：{vote_cnt}回目の成功失敗:",description=f"{sql}\n成功の場合 : .s\n失敗の場合 : .f\nを入力してください")
                                            await msg.send(embed=embed)

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
                                        sql = f"選出メンバー："
                                        for i in range(quest_member_num[game_member_num][quest_cnt-1][0]):
                                            sql = f"{sql}\n{game_member[i]+1}：{avalon_user[game_member[i]][1]}"

                                        if vote_cnt == 5:
                                            sql = f"{sql}\n次の選出が却下された場合、赤陣営の勝利です。\nリーダは{avalon_user[select_member][1]}です。\n{player_display(game_member_num, avalon_user, select_member)}"
                                        embed = discord.Embed(title="投票結果",description=f"{vote_msg}\n{sql}")
                                        file = "./image/却下.jpeg"
                                        await msgch.send(embed=embed, file = File(file))
                                        sql = "クエスト情報："
                                        for i in range(5):
                                            if i+1 == quest_cnt:
                                                sql = f"{sql}\n■{i+1}クエ：{quest_member_num[game_member_num][i][0]}人"
                                            else:
                                                sql = f"{sql}\n□{i+1}クエ：{quest_member_num[game_member_num][i][0]}人"
                                            sql = f"{sql}\n成功{quest_success_cnt}\n失敗{quest_fail_cnt}"
                                            sql = f"{sql}\n選出メンバー："
                                            for i in range(quest_member_num[game_member_num][quest_cnt-1][0]):
                                                sql = f"{sql}\n{game_member[i]+1}：{avalon_user[game_member[i]][1]}"

                                            for i in range(game_member_num):
                                                msg = client.get_user(avalon_user[i][2])
                                                embed = discord.Embed(title=f"第{quest_cnt}クエスト：{vote_cnt}回目の承認却下:",description=f"{sql}\n承認の場合 : a\n却下の場合 : .r\nを入力してください")
                                                await msg.send(embed=embed)
                                    else:
                                        vote_cnt += 1
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
                                    sql = f"insert into `avalon_comment` (`user`, `comment`) \
                                    value (%s, %s)"
                                    value = ('bot', f"{quest_cnt}クエ、{vote_cnt-1}回目却下\n")
                                    db.execute(sql, value)
                    else:
                        await ctx.channel.send(f"このコマンドは無効です。：{comment}")

                elif game_phase == 2: #成功失敗フェーズ
                    command_accept = 0
                    if comment == '.s' or comment == '.f':
                        agravain_member = role_find(game_member_num, avalon_user, 15)
                        if comment == '.s':
                            command_accept = 16
                        elif comment == '.f':
                            command_accept = 8

                        n8_cnt = 0
                        if role_find(game_member_num, avalon_user, 8) != None:
                            for i in range(quest_member_num[game_member_num][quest_cnt-1][0]):
                                if avalon_user[game_member[i]][3] == 8:
                                    n8_cnt += 1
                        for i in range(quest_member_num[game_member_num][quest_cnt-1][0]):
                            num = game_member[i]
                            if ctx.author.id == avalon_user[num][2]:
                                msg = client.get_user(avalon_user[num][2])
                                if avalon_user[num][3] == 15:
                                    if command_accept == 8 and quest_success_cnt < 2:
                                        command_accept = 16
                                        await msg.send(f"成功が2回出てないため、強制的に成功へ変更しました。")
                                elif avalon_user[num][3] == 8:
                                    if command_accept == 16 and n8_cnt != 2:
                                        command_accept = 8
                                        await msg.send(f"恋人2人でクエストへ参加できなかったため、強制的に失敗へ変更しました。")
                                elif avalon_user[num][3] == 7:
                                    if(quest_cnt == 2 or quest_cnt == 4) and command_accept == 16:
                                        command_accept = 8
                                        await msg.send(f"あなたは{quest_cnt}クエストに失敗しか出せません。強制的に失敗へ変更しました。")
                                elif avalon_user[num][3] < 10:
                                    if command_accept == 8:
                                        command_accept = 16
                                        await msg.send(f"あなたは青陣営のため、強制的に成功へ変更しました。")
                                elif avalon_user[num][3] == 21:
                                    if quest_cnt%2 == 1 and command_accept == 8:
                                        command_accept = 16
                                        await msg.send(f"あなたは{quest_cnt}クエストでは青陣営のため、強制的に成功へ変更しました。")
                                    elif quest_cnt%2 == 0 and command_accept == 16:
                                        command_accept = 8
                                        await msg.send(f"あなたは{quest_cnt}クエストでは赤陣営のため、強制的に失敗へ変更しました。")

                                if avalon_quest[num] < 8:
                                    sql = f"update `avalon_quest` \
                                    set `member{num+1}` = {avalon_quest[num]+command_accept} \
                                    where id = {quest_id}"
                                    avalon_quest[num] = avalon_quest[num] + command_accept

                                    for k in range(quest_member_num[game_member_num][quest_cnt-1][0]):
                                        num = game_member[k]
                                        if k == 0:
                                            if avalon_quest[num] > 8 or num == game_member[i]:
                                                vote_msg = f"投票完了:{game_member[k]+1}:{avalon_user[game_member[k]][1]}"
                                            else:
                                                vote_msg = f"投票未完:{game_member[k]+1}:{avalon_user[game_member[k]][1]}"
                                        else:
                                            if avalon_quest[num] > 8 or num == game_member[i]:
                                                vote_msg = f"{vote_msg}\n投票完了:{game_member[k]+1}:{avalon_user[game_member[k]][1]}"
                                            else:
                                                vote_msg = f"{vote_msg}\n投票未完:{game_member[k]+1}:{avalon_user[game_member[k]][1]}"

                                    if command_accept == 16:
                                        await msg.send(f"成功を受け付けました。")
                                    else:
                                        await msg.send(f"失敗を受け付けました。")

                                else:
                                    sql = f"update `avalon_quest` \
                                    set `member{i+1}` = {avalon_quest[i]%8+command_accept} \
                                    where id = {quest_id}"
                                    avalon_quest[i] = avalon_quest[i]%8 + command_accept

                                    for k in range(quest_member_num[game_member_num][quest_cnt-1][0]):
                                        num = game_member[k]
                                        if k == 0:
                                            if avalon_quest[num] > 8 or avalon_user[num][2] == ctx.author.id:
                                                vote_msg = f"投票完了:{game_member[k]+1}:{avalon_user[game_member[k]][1]}"
                                            else:
                                                vote_msg = f"投票未完:{game_member[k]+1}:{avalon_user[game_member[k]][1]}"
                                        else:
                                            if avalon_quest[num] > 8 or avalon_user[num][2] == ctx.author.id:
                                                vote_msg = f"{vote_msg}\n投票完了:{game_member[k]+1}:{avalon_user[game_member[k]][1]}"
                                            else:
                                                vote_msg = f"{vote_msg}\n投票未完:{game_member[k]+1}クエスト履歴:{avalon_user[game_member[k]][1]}"

                                    if command_accept == 16:
                                        await msg.send(f"成功へ上書きしました。")
                                        await msgch.send(f"{ctx.author.display_name}が上書きしました。")
                                    else:
                                        await msg.send(f"失敗へ上書きしました。")
                                        await msgch.send(f"{ctx.author.display_name}が上書きしました。")

                                db.execute(sql)
                                # break

                                embed = discord.Embed(title="投票状況",description=vote_msg)
                                await msgch.send(embed=embed)

                                # judge next phase
                                fail_cnt = 0
                                success_cnt = 0
                                vote_msg = f"第{quest_cnt}クエスト："
                                member_msg = "クエスト参加メンバー"
                                for k in range(quest_member_num[game_member_num][quest_cnt-1][0]):
                                    num = game_member[k]
                                    member_msg = f"{member_msg}\n{num+1} : {avalon_user[num][1]}"
                                    if avalon_quest[num] > 8:
                                        if avalon_quest[num] < 16:
                                            fail_cnt += 1
                                        else:
                                            success_cnt += 1
                                    else:
                                        break

                                if fail_cnt + success_cnt == quest_member_num[game_member_num][quest_cnt-1][0]:
                                    for k in range(fail_cnt+success_cnt):
                                        if k < success_cnt:
                                            vote_msg = f"{vote_msg}\n成功"
                                        else:
                                            vote_msg = f"{vote_msg}\n失敗"
                                    select_member = int((select_member+1)%game_member_num)

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
                                        kill_flag = 0
                                        for k in range(game_member_num):
                                            if avalon_user[k][3] == 0:
                                                kill_flag = 1
                                                break

                                        n8_cnt = 0
                                        if role_find(game_member_num, avalon_user, 8) != None:
                                            for l in range(game_member_num):
                                                if avalon_user[l][3] == 8:
                                                    n8_cnt += 1

                                        if n8_cnt == 2:
                                            kill_flag = 1

                                        if kill_flag == 1:
                                            if role_find(game_member_num, avalon_user, 31) == None:
                                                sql = f"update `avalon_data` set \
                                                `game_status`= 3, \
                                                `game_role`= 1, \
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
                                                kill_member = role_find(game_member_num, avalon_user, 12)
                                                if kill_member == None:
                                                    kill_member = role_find(game_member_num, avalon_user, 16)
                                                if kill_member == None:
                                                    kill_member = role_find(game_member_num, avalon_user, 11)
                                                if kill_member == None:
                                                    kill_member = role_find(game_member_num, avalon_user, 10)
                                                msg = client.get_user(avalon_user[kill_member][2])
                                                if n8_cnt == 2:
                                                    sql = f"マーリンまたは{avalon_role[8][1]}の2人の一方を予想して暗殺してください"
                                                    sql = f"{sql}\n{player_display(game_member_num, avalon_user, game_member_num+1)}\nマーリンを暗殺するコマンド例：\n１番のプレイヤーを暗殺する場合 : .k 1\n{avalon_role[8][1]}を暗殺するコマンド例：\n１番と２番のプレイヤーを暗殺する場合 : .k 1,2"
                                                else:
                                                    sql = "マーリンを予想して暗殺してください"
                                                    sql = f"{sql}\n{player_display(game_member_num, avalon_user, game_member_num+1)}\nコマンド例：１番のプレイヤーを暗殺する場合\n.k 1"
                                                embed.add_field(name=f"クエスト：青陣営勝利", value="暗殺者の方が暗殺するプレイヤーを検討中です。")
                                                await msgch.send(embed=embed, file=File(file))
                                            else:
                                                ex_member = role_find(game_member_num, avalon_user, 31)
                                                sql = f"update `avalon_data` set `game_phase`= 6 where id = 0"
                                                db.execute(sql)
                                                msg = client.get_user(avalon_user[ex_member][2])
                                                sql = "暗殺される人を予想してください"
                                                if n8_cnt == 2:
                                                    sql = f"{sql}\n暗殺者はマーリンまたは{avalon_role[8][1]}の2人のいずれかを予想します"
                                                    sql = f"{sql}\n{player_display(game_member_num, avalon_user, game_member_num+1)}\nマーリンを暗殺すると思う場合のコマンド例：\n１番のプレイヤーを暗殺すると予想する場合 : .s 1\n{avalon_role[8][1]}を暗殺すると思う場合のコマンド例：\n１番と２番のプレイヤーを暗殺すると予想する場合 : .s 1,2"
                                                else:
                                                    sql = "{sql}\nマーリンを予想してください"
                                                    sql = f"{sql}\n{player_display(game_member_num, avalon_user, game_member_num+1)}\nコマンド例：１番のプレイヤーを暗殺すると予想する場合\n.s 1"
                                                embed.add_field(name=f"クエスト：青陣営勝利", value=f"{avalon_role[31][1]}が暗殺されるプレイヤーを予想中です")
                                                await msgch.send(embed=embed, file=File(file))
                                            embed = discord.Embed(title="クエスト：青陣営勝利",description=sql)
                                            await msg.send(embed=embed)
                                        else:
                                            sql = f"update `avalon_data` set \
                                            `game_status`= 0, \
                                            `game_role`= 1, \
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
                                            if role_find(game_member_num, avalon_user, 21) != None and quest_cnt%2 == 1:
                                                sql = f"{sql}\n奇数クエストのため、{avalon_role[21][1]}は青陣営で勝利です。"
                                            embed.add_field(name=f"クエスト：青陣営勝利",value=f"{sql}")
                                            await msgch.send(embed=embed, file=File(file))
                                        sql = f"insert into `avalon_comment` (`user`, `comment`) \
                                        value (%s, %s)"
                                        value = ('bot', f"{quest_cnt-1}クエ：成功\n")
                                        db.execute(sql, value)

                                    elif quest_fail_cnt == 3:
                                        game_phase = 0
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
                                        if role_find(game_member_num, avalon_user, 33) != None:
                                            num = int(role_find(game_member_num, avalon_user, 33))
                                            dbsql = 'select * from `avalon_quest`'
                                            db.execute(dbsql)
                                            rows = db.fetchall()
                                            fail_num = 0
                                            sel_num = 0
                                            for i in rows:
                                                if i[num+1]%2 == 1:
                                                    for l in range(game_member_num):
                                                        if rows[l+1] > 8:
                                                            sel_num += 1
                                                        if rows[l+1] < 16 and rows[l+1] > 8:
                                                            fail_num += 1

                                        if role_find(game_member_num, avalon_user, 32) != None:
                                            num32 = int(role_find(game_member_num, avalon_user, 32))
                                            if avalon_quest[num32+1]%2 == 1:
                                                if role_find(game_member_num, avalon_user, 33) != None :
                                                    if sel_num == 0:
                                                        sql = f"{sql}\n最終失敗クエストに参加していた{avalon_user[num32][1]}とクエストに一度も参加していない{avalon_user[num][1]}の勝利です。"
                                                        embed.add_field(name=f"{avalon_role[num32][1]}と{avalon_role[num][1]}勝利", value=f"{sql}")
                                                    elif fail_num >= 3:
                                                        sql = f"{sql}\n最終失敗クエストに参加していた{avalon_user[num32][1]}と参加したクエストで３枚以上の失敗がでた{avalon_user[num][1]}の勝利です。"
                                                        embed.add_field(name=f"{avalon_role[num32][1]}と{avalon_role[num][1]}勝利", value=f"{sql}")
                                                    else:
                                                        sql = f"{sql}\n最終失敗クエストに参加していたため、{avalon_user[num32][1]}の単独勝利です。"
                                                        embed.add_field(name=f"{avalon_role[num32][1]}単独勝利", value=f"{sql}")
                                                else:
                                                    sql = f"{sql}\n最終失敗クエストに参加していたため、{avalon_user[num32][1]}の単独勝利です。"
                                                    embed.add_field(name=f"{avalon_role[num32][1]}単独勝利", value=f"{sql}")
                                            else:
                                                if sel_num == 0:
                                                    sql = f"{sql}\nクエストに一度も参加していない{avalon_user[num][1]}の単独勝利です。"
                                                    embed.add_field(name=f"{avalon_role[num][1]}単独勝利", value=f"{sql}")
                                                elif fail_num >= 3:
                                                    sql = f"{sql}\n参加したクエストで３枚以上の失敗がでた{avalon_user[num][1]}の単独勝利です。"
                                                    embed.add_field(name=f"{avalon_role[num][1]}単独勝利", value=f"{sql}")
                                                else:
                                                    if role_find(game_member_num, avalon_user, 21) != None and quest_cnt%2 == 0:
                                                        sql = f"{sql}\n偶数クエストのため、{avalon_role[21][1]}は赤陣営で勝利です。"
                                                    embed.add_field(name=f"クエスト：赤陣営勝利", value=f"{sql}")
                                        elif role_find(game_member_num, avalon_user, 33) != None:
                                            if sel_num == 0:
                                                sql = f"{sql}\nクエストに一度も参加していない{avalon_user[num][1]}の単独勝利です。"
                                                embed.add_field(name=f"{avalon_role[num][1]}単独勝利", value=f"{sql}")
                                            elif fail_num >= 3:
                                                sql = f"{sql}\n参加したクエストで３枚以上の失敗がでた{avalon_user[num][1]}の単独勝利です。"
                                                embed.add_field(name=f"{avalon_role[num][1]}単独勝利", value=f"{sql}")
                                            else:
                                                if role_find(game_member_num, avalon_user, 21) != None and quest_cnt%2 == 0:
                                                    sql = f"{sql}\n偶数クエストのため、{avalon_role[21][1]}は赤陣営で勝利です。"
                                                embed.add_field(name=f"クエスト：赤陣営勝利", value=f"{sql}")
                                        else:
                                            if role_find(game_member_num, avalon_user, 21) != None and quest_cnt%2 == 0:
                                                sql = f"{sql}\n偶数クエストのため、{avalon_role[21][1]}は赤陣営で勝利です。"
                                            embed.add_field(name=f"クエスト：赤陣営勝利", value=f"{sql}")
                                        await msgch.send(embed=embed, file=File(file))
                                        sql = f"insert into `avalon_comment` (`user`, `comment`) \
                                        value (%s, %s)"
                                        value = ('bot', f"{quest_cnt-1}クエ：失敗\n")
                                        db.execute(sql, value)
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
                                            await msgch.send(embed=embed, file=File(file))
                                            msg = client.get_user(avalon_user[otome_select[quest_cnt-2]][2])
                                            sql = player_display(game_member_num, avalon_user, select_member)
                                            embed = discord.Embed(title=f"通算クエスト結果",description=f"成功{quest_success_cnt}回\n失敗{quest_fail_cnt}回")
                                            embed.add_field(name="乙女選出",value=f"{sql}\nあなたは乙女選出者です。\n選出例:1番のプレイヤーに乙女を使う場合\n.s 1")
                                            await msg.send(embed=embed)
                                            sql = f"insert into `avalon_comment` (`user`, `comment`) \
                                            value (%s, %s)"
                                            if fail_cnt >= base_num:
                                                value = ('bot', f"{quest_cnt-1}クエ：失敗：乙女開始")
                                            else:
                                                value = ('bot', f"{quest_cnt-1}クエ：成功：乙女開始")
                                            db.execute(sql, value)

                                        else:
                                            fail_num = 0
                                            if fail_cnt >= base_num:
                                                if role_find(game_member_num, avalon_user, 33) != None:
                                                    num = int(role_find(game_member_num, avalon_user, 33))
                                                    dbsql = 'select * from `avalon_quest`'
                                                    db.execute(dbsql)
                                                    rows = db.fetchall()
                                                    for l in rows:
                                                        if l[num+1]%2 == 1:
                                                            for m in range(game_member_num):
                                                                if int(rows[m+1]) < 16 and int(rows[m+1]) > 8:
                                                                    fail_num += 1
                                            if fail_num >= 3:
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
                                                num = int(role_find(game_member_num, avalon_user, 33))

                                                if role_find(game_member_num, avalon_user, 32) != None:
                                                    if avalon_quest[num+1]%2 == 1:
                                                        sql = f"{sql}\n最終失敗クエストに参加していたため、{avalon_user[int(role_find(game_member_num, avalon_user, 32))][1]}と{avalon_user[int(role_find(game_member_num, avalon_user, 33))][1]}の勝利です。"
                                                        embed.add_field(name=f"{avalon_role[32][1]}と{avalon_role[33][1]}勝利", value=f"{sql}")
                                                    else:
                                                        sql = f"{sql}\n{avalon_user[int(role_find(game_member_num, avalon_user, 33))][1]}の単独勝利です。"
                                                        embed.add_field(name=f"{avalon_role[33][1]}単独勝利", value=f"{sql}")
                                                else:
                                                    sql = f"{sql}\n{avalon_user[int(role_find(game_member_num, avalon_user, 33))][1]}の単独勝利です。"
                                                    embed.add_field(name=f"{avalon_role[33][1]}単独勝利", value=f"{sql}")
                                                await msgch.send(embed=embed, file=File(file))
                                                sql = f"insert into `avalon_comment` (`user`, `comment`) \
                                                value (%s, %s)"
                                                value = ('bot', f"{quest_cnt-1}クエ：失敗\n\nゲーム終了")
                                                db.execute(sql, value)
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
                                                msg = client.get_user(avalon_user[select_member][2])
                                                await msg.send(embed=embed)
                                                sql = player_display(game_member_num, avalon_user, select_member)
                                                embed.add_field(name=f"第{quest_cnt}クエスト：{vote_cnt}回目の選出:",value=f"リーダは{avalon_user[select_member][1]}です。\n{sql}")
                                                await msgch.send(embed=embed, file=File(file))
                                                msg = client.get_user(avalon_user[select_member][2])
                                                sql = f"あなたはリーダです。\n{quest_member_num[game_member_num][quest_cnt-1][0]}人選出してください\n1番〜3番の3人の選出例：.s 1,2,3\n{player_display(game_member_num, avalon_user, select_member)}"
                                                embed = discord.Embed(title=f"第{quest_cnt}クエスト：{vote_cnt}回目の選出:",description=sql)
                                                await msg.send(embed=embed)
                                                sql = f"insert into `avalon_comment` (`user`, `comment`) \
                                                value (%s, %s)"
                                                if fail_cnt >= base_num:
                                                    value = ('bot', f"{quest_cnt-1}クエ：失敗\n")
                                                else:
                                                    value = ('bot', f"{quest_cnt-1}クエ：成功\n")
                                                db.execute(sql, value)
                    else:
                        await ctx.channel.send(f"このコマンドは無効です。：{comment}")

                elif game_phase == 4: #乙女フェーズ
                    otome_select = [game_otome1, game_otome2, game_otome3]
                    otome_member = otome_select[quest_cnt-2]
                    if comment[0:3] == '.s ':
                        if ctx.author.id == avalon_user[otome_member][2]:
                            select_member_com = re.compile('\d+')
                            select_member_match = select_member_com.findall(comment)
                            # 重複チェック
                            if len(select_member_match) != 1:
                                await ctx.author.send(f"選択人数は1人です：{comment}")
                            else :
                                otome_check = 0
                                otome_num = int(select_member_match[0])-1
                                for i in range(quest_cnt-1):
                                    if otome_select[i] == None:
                                        break
                                    elif otome_num == otome_select[i]:
                                        otome_check = 1
                                        break

                                flg=0
                                if otome_check == 0 and otome_num >= 0 and otome_num < game_member_num:
                                    msg = client.get_user(avalon_user[otome_num][2])
                                    await msg.send("あなたに乙女が使用されました。")
                                    if avalon_user[otome_num][3] < 10 or avalon_user[otome_num][3] == 30:
                                        otome_msg = f"{avalon_user[otome_num][1]}は青陣営です"
                                        file="./image/忠誠カード青.jpeg"
                                        flg = 1
                                    elif avalon_user[otome_num][3] <20:
                                        otome_msg = f"{avalon_user[otome_num][1]}は赤陣営です"
                                        file="./image/忠誠カード赤.jpeg"
                                        flg = 1
                                    elif avalon_user[otome_num][3] == 21:
                                        if quest_cnt%2 == 1:
                                            otome_msg = f"{avalon_user[otome_num][1]}は青陣営です。"
                                            file="./image/忠誠カード青.jpeg"
                                        else:
                                            otome_msg = f"{avalon_user[otome_num][1]}は赤陣営です。"
                                            file="./image/忠誠カード赤.jpeg"
                                        flg = 1
                                    elif avalon_user[otome_num][3] <30:
                                        otome_msg = f"{avalon_user[otome_num][1]}はどちらの陣営でもありません"
                                        flg = 0
                                    else:
                                        otome_msg = f"{avalon_user[otome_num][1]}は青陣営です"
                                        file="./image/忠誠カード青.jpeg"
                                        flg = 1
                                    embed = discord.Embed(title="乙女結果",description=otome_msg)
                                    if flg == 1:
                                        await ctx.author.send(embed=embed, file=File(file))
                                    else:
                                        await ctx.author.send(embed=embed)

                                    game_phase = 0
                                    quest_cnt += 1
                                    vote_cnt = 1
                                    select_member += 1
                                    if quest_cnt != 5:
                                        sql = f"update `avalon_data` set \
                                        `game_phase`= {game_phase}, \
                                        `select_member`= {select_member}, \
                                        `quest_cnt`= {quest_cnt}, \
                                        `vote_cnt` = {vote_cnt}, \
                                        `game_otome{quest_cnt-1}` = {otome_num} \
                                        where id = 0"
                                    else:
                                        sql = f"update `avalon_data` set \
                                        `game_phase`= {game_phase}, \
                                        `select_member`= {select_member}, \
                                        `quest_cnt`= {quest_cnt}, \
                                        `vote_cnt` = {vote_cnt} \
                                        where id = 0"
                                    db.execute(sql)
                                    sql = player_display(game_member_num, avalon_user, select_member)
                                    embed = discord.Embed(title=f"第{quest_cnt}クエスト：{vote_cnt}回目の選出:",description=f"リーダは{avalon_user[select_member][1]}です。\n{sql}")
                                    await msgch.send(f"乙女を{avalon_user[otome_num][1]}に使用しました。", embed=embed)
                                    msg = client.get_user(avalon_user[select_member][2])
                                    sql = f"あなたはリーダです。\n{quest_member_num[game_member_num][quest_cnt-1][0]}人選出してください\n1番〜3番の3人の選出例：.s 1,2,3\n{player_display(game_member_num, avalon_user, select_member)}"
                                    embed = discord.Embed(title=f"第{quest_cnt}クエスト：{vote_cnt}回目の選出:",description=sql)
                                    await msg.send(embed=embed)
                                    sql = f"insert into `avalon_comment` (`user`, `comment`) \
                                    value (%s, %s)"
                                    value = ('bot', f"{quest_cnt-2}回目：乙女使用\n")
                                    db.execute(sql, value)
                                else:
                                    if otome_check == 0:
                                        await ctx.author.send(f"選択番号は1〜{game_member_num}にしてください")
                                    else:
                                        if otome_member == otome_num:
                                            await ctx.author.send(f"乙女選出者(自分)は選出できません。")
                                        else:
                                            await ctx.author.send(f"乙女使用者は選出できません。")
                        else:
                            await ctx.channel.send(f"あなたは乙女の選出者ではありません。")
                    else:
                        await ctx.channel.send(f"このコマンドは無効です。：{comment}")

                elif game_phase == 5: #ビースト能力(オベロン化)フェーズ
                    # select : 選択
                    for i in range(game_member_num) :
                        if avalon_user[i][3] == 16:
                            beast_num = i
                            msg = client.get_user(avalon_user[i][2])

                    if comment[0:3] == '.s ':
                        if ctx.author.id == avalon_user[beast_num][2]:
                            select_member_com = re.compile('\d+')
                            select_member_match = select_member_com.findall(comment)
                            # 重複チェック
                            if len(select_member_match) != 1:
                                await ctx.author.send(f"選択人数は1人です：{comment}")
                            else :
                                select_check = 0
                                select_num = int(select_member_match[0])-1
                                if select_num == beast_num:
                                    await ctx.author.send("自分をオベロンにすることはできません。\nあなた以外を選択してください。")
                                elif select_num >= 0 and select_num <= game_member_num-1:
                                    msg = client.get_user(avalon_user[select_num][2])
                                    await msg.send("あなたは選択されたため、オベロンになりました。\n1回目の通知の役職は無効となります。", file = File(avalon_role[14][2]))
                                    if avalon_user[select_num][3] == 0:
                                        avalon_user[select_num][3] = 14
                                        sql = f"update `avalon_user` set `role` = 14 where `id` = {select_num+1}"
                                        db.execute(sql)
                                        for i in range(game_member_num):
                                            if avalon_user[i][3] != 1:
                                                continue
                                            else:
                                                msg = client.get_user(avalon_user[i][2])
                                                await msg.send("マーリンがオベロンになってしまいました。\nよってあなたがマーリンに昇格します。\n1回目の通知の役職は無効となります。", file = File(avalon_role[0][2]))
                                                avalon_user[i][3] = 0

                                                sql = f"update `avalon_user` set `role` = 0 where `id` = {i+1}"
                                                db.execute(sql)
                                    elif avalon_user[select_num][3] == 8:
                                        avalon_user[select_num][3] = 14
                                        sql = f"update `avalon_user` set `role` = 14 where `id` = {select_num+1}"
                                        db.execute(sql)
                                        # 情弱
                                        lover_change_member = role_find(game_member_num, avalon_user, 3)
                                        if lover_change_member == None:
                                            # ガウェイン
                                            lover_change_member = role_find(game_member_num, avalon_user, 7)
                                            if lover_change_member == None:
                                                # カラドック
                                                lover_change_member = role_find(game_member_num, avalon_user, 6)
                                                if lover_change_member == None:
                                                    # ガラハッド
                                                    lover_change_member = role_find(game_member_num, avalon_user, 2)
                                                    if lover_change_member == None:
                                                        # パーシヴァル
                                                        lover_change_member = role_find(game_member_num, avalon_user, 1)

                                        avalon_user[lover_change_member][3] = 8
                                        sql = f"update `avalon_user` set `role` = 8 where `id` = {lover_change_member+1}"
                                        db.execute(sql)
                                        msg = client.get_user(avalon_user[lover_change_member][2])
                                        await msg.send(f"{avalon_role[8][1]}の1人がオベロンになってしまいました。\nよってあなたが{avalon_role[8][1]}に変更となります。\n1回目の通知の役職は無効となります。", file = File(avalon_role[8][2]))
                                    else:
                                        avalon_user[select_num][3] = 14
                                        sql = f"update `avalon_user` set `role` = 14 where `id` = {select_num+1}"
                                        db.execute(sql)

                                    for i in range(game_member_num):
                                        msg = client.get_user(avalon_user[i][2])
                                        await msg.send(f"あなたの最終役職は{avalon_role[avalon_user[i][3]][1]}です。")
                                        if avalon_user[i][3] == 0 : # マーリン
                                            role_info = '赤陣営は\n'
                                            flg = 0
                                            for j in range(game_member_num):
                                                if ((avalon_user[j][3] >= 11 and avalon_user[j][3] <= 16) or avalon_user[j][3] == 6) and avalon_user[j][3] != 15:
                                                    role_info = f"{role_info}\n{j+1}：{avalon_user[j][1]}"
                                                    if avalon_user[j][3] == 6:
                                                        flg = 1
                                            role_info = f"{role_info}\nです。\nバレないようにクエスト勝利へ導いてください。"
                                            if flg == 1:
                                                role_info = f"{role_info}\nカラドックは赤陣営として通知されます。※ローカル拡張役職です。"
                                            await msg.send(f"{role_info}")
                                        elif avalon_user[i][3] == 1 : # パーシヴァル
                                            role_info = 'マーリンとモルガナを確認することができます。\n'
                                            for j in range(game_member_num):
                                                if avalon_user[j][3] == 0 or avalon_user[j][3] == 11:
                                                    role_info = f"{role_info}\n{j+1}：{avalon_user[j][1]}"
                                            role_info = f"{role_info}\nがマーリンとモルガナです。\n役職によって2人とは限りません。"
                                            await msg.send(f"{role_info}")
                                        elif avalon_user[i][3] == 2 : # ガラハッド
                                            role_info = f"パーシヴァルと暗殺者と{avalon_role[16][1]}を確認することができます。\n"
                                            for j in range(game_member_num):
                                                if (avalon_user[j][3] == 1 or avalon_user[j][3] == 12 or avalon_user[j][3] == 16):
                                                    role_info = f"{role_info}\n{j+1}：{avalon_user[j][1]}"
                                            role_info = f"{role_info}\n役職によって3人とは限りません。"
                                            await msg.send(f"{role_info}")
                                        elif avalon_user[i][3] == 6 : # カラドック
                                            role_info = f"青陣営ですが、マーリンに赤として通知されます。\n※ローカル拡張役職です。"
                                            await msg.send(f"{role_info}")
                                        elif avalon_user[i][3] == 8 : # 恋人
                                            role_info = "恋人同士は"
                                            for j in range(game_member_num):
                                                if avalon_user[j][3] == 8:
                                                    role_info = f"{role_info}\n{j+1}：{avalon_user[j][1]}"
                                            role_info = f"{role_info}\nです。\n暗殺者に恋人同士の2人が暗殺されてしまうと、負けてしまいます。\nバレないようにプレイしてください。\n※ローカル拡張役職です。"
                                            await msg.send(f"{role_info}")
                                        elif (avalon_user[i][3] >= 10 and avalon_user[i][3] <= 19) and avalon_user[i][3] != 14 and avalon_user[i][3] != 15: # 赤陣営
                                            role_info = '赤陣営は\n'
                                            for j in range(game_member_num):
                                                if (avalon_user[j][3] >= 10 and avalon_user[j][3] <= 19) and avalon_user[j][3] != 14 and avalon_user[j][3] != 15:
                                                    role_info = f"{role_info}\n{j+1}：{avalon_user[j][1]}"
                                            role_info = f"{role_info}\nです。"
                                            if role_find(game_member_num, avalon_user, 14) != None:
                                                if role_find(game_member_num, avalon_user, 15) != None:
                                                    role_info = f"{role_info}\nただし{avalon_role[14][1]}と{avalon_role[15][1]}は見えません。"
                                                else:
                                                    role_info = f"{role_info}\nただし{avalon_role[14][1]}は見えません。"
                                            else:
                                                if role_find(game_member_num, avalon_user, 15) != None:
                                                    role_info = f"{role_info}\nただし{avalon_role[15][1]}は見えません。"
                                            await msg.send(f"{role_info}")
                                        elif avalon_user[i][3] == 14 : # 赤陣営
                                            role_info = 'あなたは仲間の赤陣営を知りません。'
                                            if role_find(game_member_num, avalon_user, 15) != None:
                                                role_info = f"{role_info}\n{avalon_role[15][1]}を除いて赤陣営はあなたを知りません。"
                                            else:
                                                role_info = f"{role_info}\n赤陣営はあなたを知りません。"
                                            await msg.send(f"{role_info}")
                                        elif avalon_user[i][3] == 15: # 赤陣営
                                            role_info = '赤陣営は\n'
                                            for j in range(game_member_num):
                                                if avalon_user[j][3] >= 10 and avalon_user[j][3] <= 19:
                                                    role_info = f"{role_info}\n{j+1}：{avalon_user[j][1]}"
                                            role_info = f"{role_info}\nです。"
                                            await msg.send(f"{role_info}")
                                        elif avalon_user[i][3] >= 30 and avalon_user[i][3] <= 33: # 赤陣営
                                            if avalon_user[i][3] == 31:
                                                role_info = f"あなたは情報を知りません。\n勝利条件は暗殺フェーズ直前に暗殺されるプレイヤーを予想し、当てることです"
                                            else:
                                                role_info = '赤陣営は\n'
                                                for j in range(game_member_num):
                                                    if (avalon_user[j][3] >= 10 and avalon_user[j][3] < 20):
                                                        role_info = f"{role_info}\n{j+1}：{avalon_user[j][1]}"
                                                if avalon_user[i][3] == 30:
                                                    role_info = f"{role_info}\nです。\n勝利条件は暗殺されることです。"
                                                elif avalon_user[i][3] == 32:
                                                    role_info = f"{role_info}\nです。\n3回目の失敗でクエストに参加していると単独勝利します。\n{avalon_role[33][1]}の勝利条件と同時成立した場合、同時勝利です。"
                                                elif avalon_user[i][3] == 33:
                                                    role_info = f"{role_info}\nです。\n一度もクエストに選ばれない、または参加したクエストの失敗数の累計が3枚以上の場合、単独勝利します。\n{avalon_role[32][1]}の勝利条件と同時成立した場合、同時勝利です。"
                                            await msg.send(f"{role_info}")

                                    role = [1]*game_member_num
                                    for i in range(game_member_num):
                                        role[i] = avalon_user[i][3]
                                    role.sort()
                                    sql = f"{game_member_num}人戦のクエスト："
                                    for i in range(5):
                                        sql = f"{sql}\n{i+1}クエ：{quest_member_num[game_member_num][i][0]}人"
                                    embed = discord.Embed(title=f"ゲーム開始",description=sql)
                                    sql = "役職："
                                    for i in range(game_member_num):
                                        sql = f"{sql}\n{avalon_role[role[i]][1]}"
                                    embed.add_field(name=f"役職",value=sql)
                                    sql = f"現在の状況：\n成功{quest_success_cnt}\n失敗{quest_fail_cnt}\nリーダは{avalon_user[select_member][1]}です。\n{player_display(game_member_num, avalon_user, select_member)}"
                                    embed.add_field(name=f"第{quest_cnt}クエスト：{vote_cnt}回目の選出:",value=sql)
                                    await msgch.send(embed=embed)
                                    msg = client.get_user(avalon_user[select_member][2])
                                    sql = f"あなたはリーダです。\n{quest_member_num[game_member_num][quest_cnt-1][0]}人選出してください\n1番〜3番の3人の選出例：.s 1,2,3\n{player_display(game_member_num, avalon_user, select_member)}"
                                    embed = discord.Embed(title=f"第{quest_cnt}クエスト：{vote_cnt}回目の選出:",description=sql)
                                    await msg.send(embed=embed)
                                    sql = f"insert into `avalon_comment` (`user`, `comment`) \
                                    value (%s, %s)"
                                    value = ('bot', f"{quest_cnt}クエ、{vote_cnt}回目")
                                    db.execute(sql, value)
                                    game_phase = 0
                                    sql = f"update `avalon_data` set `game_phase`={game_phase} where id = 0"
                                    db.execute(sql)
                                else:
                                    await ctx.author.send(f"選出番号は1〜{game_member_num}から選んでください。：{comment}")
                        else:
                            await ctx.author.send(f"あなたは{avalon_role[16][1]}ではありません。")
                    else:
                        await ctx.channel.send(f"このコマンドは無効です。：{comment}")
                # 漁夫王 暗殺予想フェーズ
                elif game_phase == 6:

                    n8_cnt = 0
                    if role_find(game_member_num, avalon_user, 8) != None:
                        for i in range(game_member_num):
                            if avalon_user[i][3] == 8:
                                n8_cnt += 1

                    ex_member = role_find(game_member_num, avalon_user, 31)
                    msg = client.get_user(avalon_user[ex_member][2])
                    # select : 選択
                    if comment[0:3] == '.s ':
                        if ctx.author.id == avalon_user[ex_member][2]:
                            select_member_com = re.compile('\d+')
                            select_member_match = select_member_com.findall(comment)
                            # 重複チェック
                            if len(select_member_match) == 1:
                                select_check = 0
                                select_num = int(select_member_match[0])-1
                                if select_num >= 0 and select_num <= game_member_num-1:
                                    if n8_cnt == 2:
                                        sql = f"alter table `avalon_data` add `ex_kill_member1` int"
                                        db.execute(sql)
                                        sql = f"alter table `avalon_data` add `ex_kill_member2` int"
                                        db.execute(sql)
                                        sql = f"update `avalon_data` set `ex_kill_member1` = {select_num} where `id` = 0"
                                        db.execute(sql)
                                        await ctx.author.send(f"{select_num+1}の{avalon_user[select_num][1]}を選択しました。")
                                    else:
                                        sql = f"alter table `avalon_data` add `ex_kill_member` int"
                                        db.execute(sql)
                                        sql = f"update `avalon_data` set `ex_kill_member` = {select_num} where `id` = 0"
                                        db.execute(sql)
                                        await ctx.author.send(f"{select_num+1}の{avalon_user[select_num][1]}を選択しました。")
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
                                    kill_member = role_find(game_member_num, avalon_user, 12)
                                    if kill_member == None:
                                        kill_member = role_find(game_member_num, avalon_user, 16)
                                    if kill_member == None:
                                        kill_member = role_find(game_member_num, avalon_user, 11)
                                    if kill_member == None:
                                        kill_member = role_find(game_member_num, avalon_user, 10)
                                    msg = client.get_user(avalon_user[kill_member][2])
                                    if n8_cnt == 2:
                                        sql = f"マーリンまたは{avalon_role[8][1]}の2人の一方を予想して暗殺してください"
                                        sql = f"{sql}\n{player_display(game_member_num, avalon_user, game_member_num+1)}\nマーリンを暗殺するコマンド例：\n１番のプレイヤーを暗殺する場合 : .k 1\n{avalon_role[8][1]}を暗殺するコマンド例：\n１番と２番のプレイヤーを暗殺する場合 : .k 1,2"
                                    else:
                                        sql = "マーリンを予想して暗殺してください"
                                        sql = f"{sql}\n{player_display(game_member_num, avalon_user, game_member_num+1)}\nコマンド例：１番のプレイヤーを暗殺する場合\n.k 1"
                                    await msg.send(sql)
                                    embed = discord.Embed(title=f"クエスト：青陣営勝利",description="暗殺者の方が暗殺者を検討中です。")
                                    await msgch.send(embed=embed)
                            if len(select_member_match) == 2 and n8_cnt == 2:
                                select_check = 0
                                select_num = [int(select_member_match[0])-1,int(select_member_match[1])-1]
                                err_flg = 0
                                for i in range(2):
                                    if select_num[i] >= 0 and select_num[i] <= game_member_num-1:
                                        continue
                                    else:
                                        err_flg = 1

                                if err_flg == 0:
                                    sql = f"alter table `avalon_data` add `ex_kill_member1` int"
                                    db.execute(sql)
                                    sql = f"alter table `avalon_data` add `ex_kill_member2` int"
                                    db.execute(sql)
                                    sql = f"update `avalon_data` set `ex_kill_member1` = {select_num[0]} where `id` = 0"
                                    db.execute(sql)
                                    sql = f"update `avalon_data` set `ex_kill_member2` = {select_num[1]} where `id` = 0"
                                    db.execute(sql)
                                    await ctx.author.send(f"{avalon_role[8][1]}の暗殺予想として\n{select_num[0]+1}：{avalon_user[select_num[0]][1]}\n{select_num[1]+1}：{avalon_user[select_num[1]][1]}\nを選択しました。")
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
                                    kill_member = role_find(game_member_num, avalon_user, 12)
                                    if kill_member == None:
                                        kill_member = role_find(game_member_num, avalon_user, 16)
                                    if kill_member == None:
                                        kill_member = role_find(game_member_num, avalon_user, 11)
                                    if kill_member == None:
                                        kill_member = role_find(game_member_num, avalon_user, 10)
                                    msg = client.get_user(avalon_user[kill_member][2])
                                    if n8_cnt == 2:
                                        sql = f"マーリンまたは{avalon_role[8][1]}の2人の一方を予想して暗殺してください"
                                        sql = f"{sql}\n{player_display(game_member_num, avalon_user, game_member_num+1)}\nマーリンを暗殺するコマンド例：\n１番のプレイヤーを暗殺する場合 : .k 1\n{avalon_role[8][1]}を暗殺するコマンド例：\n１番と２番のプレイヤーを暗殺する場合 : .k 1,2"
                                    else:
                                        sql = "マーリンを予想して暗殺してください"
                                        sql = f"{sql}\n{player_display(game_member_num, avalon_user, game_member_num+1)}\nコマンド例：１番のプレイヤーを暗殺する場合\n.k 1"
                                    await msg.send(sql)
                                    embed = discord.Embed(title=f"クエスト：青陣営勝利",description="暗殺者の方が暗殺者を検討中です。")
                                    await msgch.send(embed=embed)
                                else:
                                    await ctx.author.send(f"選出番号は1〜{game_member_num}から選んでください。：{comment}")
                            else:
                                if n8_cnt != 2:
                                    await ctx.author.send(f"選択人数は1人です：{comment}")
                                else:
                                    await ctx.author.send(f"マーリンを予想する場合には、1人選択してください。\n{avalon_role[8][1]}を予想する場合には、2人選択してください。\n：{comment}")
                        else:
                            await ctx.author.send(f"あなたは{avalon_role[31][1]}ではありません。")
                    else:
                        await ctx.channel.send(f"このコマンドは無効です。：{comment}")
                else:
                    await ctx.channel.send(f"このコマンドは無効です。：{comment}")

            elif game_status == 3:
                msgch = client.get_channel(channel_id)
                quest_id = int((quest_cnt-1)*5+vote_cnt)
                avalon_user = [[1, 'name1', 1, 1, '1'], [1, 'name2', 2, 2, '2']]
                for i in range(game_member_num) :
                    sql = f"select * from `avalon_user` where id = {i+1}"
                    db.execute(sql)
                    rows = db.fetchone()
                    avalon_user.append([0, rows[1], rows[2], rows[3], rows[4]])
                avalon_user.pop(0)
                avalon_user.pop(0)

                if comment[0:3] == '.n ':
                    cmd = comment.lstrip(".n ")
                    sql = f"insert into `avalon_comment` (`user`, `comment`) \
                    value (%s, %s)"
                    value = (f"{ctx.author.display_name}", f"{cmd}")
                    db.execute(sql, value)
                    await ctx.author.send(f"コメントを受け付けました。")

                # kill : 暗殺
                elif comment[0:3] == '.k ':
                    kill_member = role_find(game_member_num, avalon_user, 12)
                    if kill_member == None:
                        kill_member = role_find(game_member_num, avalon_user, 16)
                    if kill_member == None:
                        kill_member = role_find(game_member_num, avalon_user, 11)
                    if kill_member == None:
                        kill_member = role_find(game_member_num, avalon_user, 10)

                    n8_cnt = 0
                    if role_find(game_member_num, avalon_user, 8) != None:
                        for i in range(game_member_num):
                            if avalon_user[i][3] == 8:
                                n8_cnt += 1

                    msg = client.get_user(avalon_user[kill_member][2])
                    if ctx.author.id == avalon_user[kill_member][2]:
                        select_member = re.compile('\d+')
                        select_member_match = select_member.findall(comment)
                        if len(select_member_match) == 1:
                            select_member_num = int(select_member_match[0])-1
                            if role_find(game_member_num, avalon_user, 31) != None:
                                dbsql = f"select `ex_kill_member` from `avalon_data` where id = 0"
                                db.execute(dbsql)
                                rows = db.fetchone()
                                ex_kill_member = int(rows[0])

                            if int(select_member_match[0]) >= 0 and int(select_member_match[0]) <= game_member_num-1:
                                sql = "配役は以下の通りです。"
                                for i in range(game_member_num):
                                    sql = f"{sql}\n{i+1} : {avalon_user[i][1]} : {avalon_role[avalon_user[i][3]][1]}"

                                if role_find(game_member_num, avalon_user, 31) != None:
                                    kill_msg = f"{avalon_role[31][1]}が予想したプレイヤーは{avalon_user[ex_kill_member[0]][1]}です。"
                                    if select_member_num == kill_member:
                                        if select_member_num == ex_kill_member:
                                            kill_msg = f"{kill_msg}\n{avalon_role[31][1]}が予想したプレイヤーが暗殺されました。"
                                            kill_msg = f"{kill_msg}\n暗殺に疲れ自害しました。"
                                            embed = discord.Embed(title=f"暗殺失敗:青陣営と{avalon_role[31][1]}の勝利",description=f"{kill_msg}\n{sql}")
                                        else:
                                            kill_msg = f"{kill_msg}\n暗殺に疲れ自害しました。"
                                            kill_msg = f"{kill_msg}\n{avalon_role[31][1]}は予想を外しました。"
                                            embed = discord.Embed(title="暗殺失敗:青陣営の勝利",description=f"{kill_msg}\n{sql}")
                                    elif avalon_user[select_member_num][3] == 0:
                                        if select_member_num == ex_kill_member:
                                            kill_msg = f"{kill_msg}\n{avalon_role[31][1]}が予想したプレイヤーが暗殺されました。"
                                            kill_msg = f"{kill_msg}\n見事マーリンを当てました。"
                                            embed = discord.Embed(title=f"暗殺成功:赤陣営と{avalon_role[31][1]}の勝利",description=f"{kill_msg}\n{sql}")
                                        else:
                                            kill_msg = f"{kill_msg}\n見事マーリンを当てました。"
                                            kill_msg = f"{kill_msg}\n{avalon_role[31][1]}は予想を外しました。"
                                            embed = discord.Embed(title="暗殺成功:赤陣営の勝利",description=f"{kill_msg}\n{sql}")
                                    else:
                                        if select_member_num == ex_kill_member:
                                            kill_msg = f"{kill_msg}\n{avalon_role[31][1]}が予想したプレイヤーが暗殺されました。"
                                            kill_msg = f"{kill_msg}\nマーリンを暗殺できませんでした。"
                                            embed = discord.Embed(title="暗殺失敗:青陣営と{avalon_role[31][1]}の勝利",description=f"{kill_msg}\n{sql}")
                                        else:
                                            kill_msg = f"{kill_msg}\nマーリンを暗殺できませんでした。"
                                            kill_msg = f"{kill_msg}\n{avalon_role[31][1]}は予想を外しました。"
                                            embed = discord.Embed(title="暗殺失敗:青陣営の勝利",description=f"{kill_msg}\n{sql}")
                                else:
                                    if select_member_num == kill_member:
                                        kill_msg = "暗殺に疲れ自害しました。"
                                        embed = discord.Embed(title="暗殺失敗:青陣営の勝利",description=f"{kill_msg}\n{sql}")
                                    elif avalon_user[select_member_num][3] == 0:
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
                                await msg.send(f"暗殺メンバーは１〜{game_member_num}で選択してください。")
                        elif (n8_cnt == 2 and len(select_member_match) == 2):
                            sql = "配役は以下の通りです。"
                            for i in range(game_member_num):
                                sql = f"{sql}\n{i+1} : {avalon_user[i][1]} : {avalon_role[avalon_user[i][3]][1]}"
                            select_member_num = [int(select_member_match[0])-1,int(select_member_match[1])-1]
                            err_flg = 0
                            if role_find(game_member_num, avalon_user, 31) != None:
                                ex_kill_member = [0,0]
                                for i in range(2):
                                    dbsql = f"select `ex_kill_member{i+1}` from `avalon_data` where id = 0"
                                    db.execute(dbsql)
                                    rows = db.fetchone()
                                    ex_kill_member[i] = int(rows[0])
                                    if int(select_member_num[i]) >= 0 and int(select_member_num[i]) <= game_member_num-1:
                                        continue
                                    else:
                                        err_flg = 1
                            if len(select_member_match) != len(set(select_member_match)):
                                err_flg = 1

                            if err_flg == 0:
                                if role_find(game_member_num, avalon_user, 31) != None:
                                    select_member_num.sort()
                                    ex_kill_member.sort()
                                    kill_msg = f"{avalon_role[31][1]}が予想したプレイヤーは{avalon_user[ex_kill_member[0]][1]}と{avalon_user[ex_kill_member[1]][1]}です。"
                                    if avalon_user[select_member_num[0]][3] == 8 and avalon_user[select_member_num[1]][3] == 8:
                                        if (select_member_num[0] == ex_kill_member[0] and select_member_num[1] == ex_kill_member[1]):
                                            kill_msg = f"{kill_msg}\n{avalon_role[31][1]}が予想したプレイヤーが暗殺されました。"
                                            kill_msg = f"{kill_msg}\n見事{avalon_role[8][1]}を2人当てました。"
                                            embed = discord.Embed(title=f"暗殺成功:赤陣営と{avalon_role[31][1]}の勝利",description=f"{kill_msg}\n{sql}")
                                        else:
                                            kill_msg = f"{kill_msg}\n見事{avalon_role[8][1]}を2人当てました。"
                                            kill_msg = f"{kill_msg}\n{avalon_role[31][1]}は予想を外しました。"
                                            embed = discord.Embed(title="暗殺成功:赤陣営の勝利",description=f"{kill_msg}\n{sql}")
                                    else:
                                        if (select_member_num[0] == ex_kill_member[0] and select_member_num[1] == ex_kill_member[1]):
                                            kill_msg = f"{kill_msg}\n{avalon_role[31][1]}が予想したプレイヤーが暗殺されました。"
                                            kill_msg = f"{kill_msg}\nマーリンを暗殺できませんでした。"
                                            embed = discord.Embed(title="暗殺失敗:青陣営と{avalon_role[31][1]}の勝利",description=f"{kill_msg}\n{sql}")
                                        else:
                                            kill_msg = f"{kill_msg}\n{avalon_role[8][1]}を2人暗殺できませんでした。"
                                            kill_msg = f"{kill_msg}\n{avalon_role[31][1]}は予想を外しました。"
                                            embed = discord.Embed(title="暗殺失敗:青陣営の勝利",description=f"{kill_msg}\n{sql}")
                                else:
                                    if avalon_user[select_member_num[0]][3] == 8 and avalon_user[select_member_num[1]][3] == 8:
                                        kill_msg = f"見事{avalon_role[8][1]}を2人当てました。"
                                        embed = discord.Embed(title="暗殺成功:赤陣営の勝利",description=f"{kill_msg}\n{sql}")
                                    else:
                                        kill_msg = f"{avalon_role[8][1]}を2人暗殺できませんでした。"
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
                                if int(select_member_match[0]) >= 0 and int(select_member_match[0]) <= game_member_num-1:
                                    await msg.send(f"暗殺メンバーは１〜{game_member_num}で選択してください。")
                                else:
                                    await msg.send(f"{avalon_role[8][1]}を暗殺する場合、異なる2人を選択してください。")
                        else:
                            if n8_cnt == 2:
                                msg.send("マーリンを暗殺する場合、1人だけ選択してください。\n1番のプレイヤーを暗殺する場合：　.k 1\n恋人の2人を暗殺する場合、2人を選択してください。\n１番と２番のプレイヤーを暗殺したい場合：　.k 1,2")
                            else:
                                msg.send("暗殺メンバーは１人です。\nプレイヤー1を暗殺する場合：　.k 1")
                else:
                    await ctx.channel.send(f"このコマンドは無効です。：{comment}")
            else:
                await ctx.channel.send(f"このコマンドは無効です。：{comment}")


# 60秒に一回ループ
@tasks.loop(seconds=60)
async def loop():
    # 現在の時刻
    now = datetime.now().strftime('%H:%M')
    day = datetime.now().strftime('%w')
    channel = client.get_channel(646047618849439744)
    if now == '21:00':
        if day == '3':
            await channel.send('@everyone 今日は水曜日です。\nアヴァロンやりませんか？')
    elif now == '22:00':
        if day == '2':
            await channel.send('@everyone 明日は水曜日です。\nアヴァロンやりませんか？')
        elif day == '3':
            await channel.send('@everyone ☆☆アヴァロンの時間です☆☆')


#ループ処理実行
loop.start()

client.run(TOKEN)
