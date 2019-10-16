import discord
import asyncio
#import MySQLdb

#int number

client = discord.Client()
token = "DISCORD_BOT_TOKEN"

#Usage_avalon="""
# コマンド
#   m      : 村作成
#   n      : コメント
#   s      : 成功
#   f      : 失敗
#   v      : 承認
#   r      : 却下
#"""

#################################
# SQL文
#################################
# 新規登録
#createSQL= \
#    "INSERT INTO \
#        loan_user_data ( \
#            username,\
#            loan,\
#            datecreated,\
#            updatedate\
#        ) \
#        VALUES( \
#            %s,\
#            %s,\
#            now(),\
#            now() \
#        )"
# データ更新
#updateSQL= \
#    "UPDATE \
#        loan_user_data \
#    SET \
#        loan = %s ,\
#        updatedate = now() \
#    WHERE \
#        username = %s "

#################################
# ログイン時のアクション
#################################
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    #################################
    # ヘルプコマンド:?help
    #################################
#    if message.content.startswith("h"):
#        if client.user != message.author:
#            m = Usage_avalon
#            await client.send_message(message.channel, m)

#################################
# DB接続処理
#################################
#def get_dbconnect():
#    for cnt in range( 1, 4 ):
#        try:
#            connector = MySQLdb.connect( host="us-cdbr-iron-east-02.cleardb.net", db="heroku_0b2656996c2477a", user="b600998caa803a", passwd="7d7aec23", charset="utf8")
#            cur = connector.cursor()
#            break
#        except Exception as e:
#            print("DB接続に失敗しました。[" + str(cnt)  + "回目]" )
#    else:
#        print("DB接続に3回失敗しました。")
#        raise
#
#    return connector,cur

client.run(token)
