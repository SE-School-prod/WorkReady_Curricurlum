"""
@file main.py
@date 2025/02/28(金)
@author 藤原光基
@brief 各bot実行用bot
@bar 編集日時 編集者 編集内容
@bar 2025/02/28(金) 藤原光基 新規作成
@bar 2025/03/07(金) 藤原光基 チケット枚数確認bot追加
"""


import os
import discord
import keep_alive


from discord.ext import tasks, commands
from settings.settings_dict import settings_dict
from src.assign_mentor_roll import assign_mentor_roll
from src.assign_course_roll import assign_course_roll
from src.manage_ticket import confirm_ticket
from src.logger import Logger


bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())
client = discord.Client(intents=discord.Intents.all())


def main():

    logger = Logger()
    logger = logger.get()

    # メンバー参加時イベントハンドラ
    @bot.event
    async def on_member_join(member):
        logger.info(f"member: {member}")
        await assign_mentor_roll(member)
        await assign_course_roll(member)

    # チャンネルにメッセージ送信時イベントハンドラ
    @bot.event
    async def on_message(message):
        logger.info(f"message: {message}")
        logger.info(f"content: {message.content}")

        # 任意のチャンネルでチャットを入力したユーザがBotもしくは運営の場合は処理をスキップする。
        if (    (message.author.display_name[-3:] != "@運営")
            and (message.author.id != settings_dict["GUILD"]["BOT_ID"])):

            # チケット購入チャンネル
            # TODO 講師単位に応じて分けられるよう調整が必要
            if message.channel.id == settings_dict["GUILD"]["CHANNEL"]["BUY_TICKET"]["ID"]:
                await confirm_ticket(message)

    # チャンネルのメッセージ編集時時イベントハンドラ
    @bot.event
    async def on_message_edit(before, after):
        logger.info(f"message(before): {before}, content: {before.content}")
        logger.info(f"message(after): {after}, content: {after.content}")

        # 任意のチャンネルでチャットを入力したユーザがBotもしくは運営の場合は処理をスキップする。
        if (    (after.author.display_name[-3:] != "@運営")
            and (after.author.id != settings_dict["GUILD"]["BOT_ID"])):

            # チケット購入チャンネル
            # TODO 講師単位に応じて分けられるよう調整が必要
            if after.channel.id == settings_dict["GUILD"]["CHANNEL"]["BUY_TICKET"]["ID"]:
                await confirm_ticket(after)


if __name__ == "__main__":
    main()
    keep_alive.keep_alive()
    bot.run(os.environ["DISCORD_TOKEN"])
